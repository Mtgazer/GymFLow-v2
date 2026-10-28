"""Member Service handling domain business logic, validation,
and integration with data structures (Dictionary index, Undo Stack, Activity Queue).
"""
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from core.data_structures import ActivityLog, ActivityQueue, MemberLookupIndex, UndoAction, UndoStack
from data.database import Database
from models import Member, Plan
from repositories.member_repository import MemberRepository
from repositories.plan_repository import PlanRepository


class MemberService:
    """Business logic service for managing members and subscriptions.
    Demonstrates Layered Architecture and utilizes domain-specific data structures:
    - MemberLookupIndex (Dictionary) for O(1) lookups
    - UndoStack (Stack) for LIFO reversal of actions
    - ActivityQueue (Queue) for FIFO audit tracking
    """

    def __init__(
        self,
        database: Optional[Database] = None,
        member_repo: Optional[MemberRepository] = None,
        plan_repo: Optional[PlanRepository] = None,
    ):
        self.db = database or Database()
        self.member_repo = member_repo or self.db.member_repo
        self.plan_repo = plan_repo or self.db.plan_repo

        # Data Structures Integration
        self.lookup_index = MemberLookupIndex()
        self.undo_stack: UndoStack[UndoAction] = UndoStack(max_capacity=50)
        self.activity_queue = ActivityQueue()

        # Prime the in-memory lookup index
        self._refresh_index()

    def _refresh_index(self):
        """Populates the in-memory dictionary index from storage."""
        try:
            members = self.member_repo.get_members_display()
            self.lookup_index.rebuild(members)
        except Exception:
            pass

    # =========================================================================
    # Validation Helpers
    # =========================================================================

    @staticmethod
    def validate_member_input(
        full_name: str, phone: str, price_paid: Union[float, str]
    ) -> Tuple[bool, str]:
        """Validates input fields prior to database operations."""
        name = full_name.strip() if full_name else ""
        if not name or len(name) < 2:
            return False, "Full name must be at least 2 characters long."

        ph = phone.strip() if phone else ""
        if not ph:
            return False, "Phone number is required."
        # Normalize: allow digits, hyphens, spaces, and leading plus
        cleaned_phone = re.sub(r"[\s\-]", "", ph)
        if not re.match(r"^\+?\d{7,15}$", cleaned_phone):
            return False, "Invalid phone number format (must contain 7-15 digits)."

        try:
            price = float(price_paid)
            if price < 0:
                return False, "Price cannot be negative."
        except (ValueError, TypeError):
            return False, "Price paid must be a valid number."

        return True, ""

    # =========================================================================
    # CRUD Operations
    # =========================================================================

    def register_member(
        self,
        full_name: str,
        phone: str,
        plan_name: str,
        price_paid: float,
        age: int = 0,
        gender: str = "Unknown",
    ) -> Tuple[bool, str]:
        """Creates a new member and assigns an initial subscription.
        Updates the in-memory dictionary index and pushes an undo action.
        """
        # 1. Validation
        valid, msg = self.validate_member_input(full_name, phone, price_paid)
        if not valid:
            return False, msg

        # 2. Check for duplicate phone in dictionary index first (O(1))
        if self.lookup_index.get_by_phone(phone.strip()):
            return False, "Phone number already exists in gym registry."

        # 3. Find plan
        plan = self.plan_repo.get_by_name(plan_name)
        if plan is None:
            return False, f"Plan '{plan_name}' not found."

        # 4. Create member in database
        member = Member(
            full_name=full_name.strip(),
            phone=phone.strip(),
            age=age,
            gender=gender,
            plan=plan.name,
        )
        try:
            member_id = self.member_repo.add(member)
            member.id = member_id
        except Exception as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                return False, "Phone number already exists."
            return False, f"Database error creating member: {e}"

        # 5. Create initial subscription
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=plan.duration_days)
        member.expiry = str(end_date)

        try:
            self.member_repo.create_subscription(
                member_id=member_id,
                plan_id=plan.id,
                start_date=start_date,
                end_date=end_date,
                payment_status="Paid",
                price_paid=float(price_paid),
            )
        except Exception as e:
            # Rollback member creation if subscription fails
            self.member_repo.delete(member_id)
            return False, f"Unable to create subscription: {e}"

        # 6. Update data structures
        self.lookup_index.put(member)

        # Enqueue audit log (FIFO Queue)
        self.activity_queue.enqueue(
            ActivityLog(
                action_type="REGISTER",
                entity_name="Member",
                entity_id=member_id,
                description=f"Registered {member.full_name} ({plan.name} plan)",
            )
        )

        # Push to Undo Stack (LIFO Stack)
        def undo_registration():
            self.member_repo.delete(member_id)
            self.lookup_index.remove(member_id)
            return True

        self.undo_stack.push(
            UndoAction(
                description=f"Register member '{member.full_name}'",
                undo_callable=undo_registration,
            )
        )

        return True, "Member registered successfully."

    def get_members(self) -> List[Member]:
        """Retrieves all members for UI display and refreshes the lookup dictionary."""
        members = self.member_repo.get_members_display()
        self.lookup_index.rebuild(members)
        return members

    def get_all_members(self) -> List[Member]:
        """Returns all members as domain objects. (Fixed previous syntax bug)."""
        return self.member_repo.get_all()

    def get_member_by_id(self, member_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves member with subscription details by ID."""
        return self.member_repo.get_by_id(member_id)

    def get_member_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Retrieves member record by phone number."""
        return self.member_repo.get_by_phone(phone)

    def edit_member(
        self,
        member_id: int,
        full_name: str,
        phone: str,
        plan_name: str,
        price_paid: float,
    ) -> Tuple[bool, str]:
        """Updates member demographic details and plan.
        Pushes previous state to UndoStack.
        """
        valid, msg = self.validate_member_input(full_name, phone, price_paid)
        if not valid:
            return False, msg

        # Snapshot current state for undo
        previous_data = self.member_repo.get_by_id(member_id)
        if not previous_data:
            return False, "Member not found."

        plan = self.plan_repo.get_by_name(plan_name)
        if plan is None:
            return False, f"Plan '{plan_name}' not found."

        success = self.member_repo.update_member_and_subscription(
            member_id=member_id,
            full_name=full_name.strip(),
            phone=phone.strip(),
            plan_id=plan.id,
            price_paid=float(price_paid),
        )

        if not success:
            return False, "Unable to update member."

        # Refresh index and enqueue log
        self._refresh_index()
        self.activity_queue.enqueue(
            ActivityLog(
                action_type="UPDATE",
                entity_name="Member",
                entity_id=member_id,
                description=f"Updated details for {full_name}",
            )
        )

        # Push to Undo Stack
        def undo_edit():
            self.member_repo.update_member_and_subscription(
                member_id=member_id,
                full_name=previous_data["full_name"],
                phone=previous_data["phone"],
                plan_id=previous_data["plan_id"],
                price_paid=previous_data["price_paid"],
            )
            self._refresh_index()
            return True

        self.undo_stack.push(
            UndoAction(
                description=f"Edit member '{full_name}'",
                undo_callable=undo_edit,
            )
        )

        return True, "Member updated successfully."

    def delete_member(self, member_id: int) -> bool:
        """Deletes a member with full undo restoration support."""
        # 1. Snapshot full member and subscription data before deletion
        member_data = self.member_repo.get_by_id(member_id)
        if not member_data:
            return False

        # 2. Perform deletion
        success = self.member_repo.delete(member_id)
        if not success:
            return False

        # 3. Update dictionary index and audit queue
        self.lookup_index.remove(member_id)
        self.activity_queue.enqueue(
            ActivityLog(
                action_type="DELETE",
                entity_name="Member",
                entity_id=member_id,
                description=f"Deleted member {member_data.get('full_name')} (ID {member_id})",
            )
        )

        # 4. Push restoration operation to Undo Stack (Stack Data Structure)
        def undo_deletion():
            self.member_repo.restore_member_with_subscription(
                member_data=member_data,
                subscription_data=member_data,
            )
            self._refresh_index()
            return True

        self.undo_stack.push(
            UndoAction(
                description=f"Delete member '{member_data.get('full_name')}'",
                undo_callable=undo_deletion,
            )
        )

        return True

    def renew_member(
        self,
        member_id: int,
        plan_name: str,
        payment_status: str,
        price_paid: float,
    ) -> Tuple[bool, str]:
        """Renews a member's subscription with calculated end date."""
        try:
            price = float(price_paid)
            if price < 0:
                return False, "Price cannot be negative."
        except (ValueError, TypeError):
            return False, "Price must be a valid number."

        plan = self.plan_repo.get_by_name(plan_name)
        if plan is None:
            return False, f"Plan '{plan_name}' not found."

        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=plan.duration_days)

        try:
            self.member_repo.create_subscription(
                member_id=member_id,
                plan_id=plan.id,
                start_date=start_date,
                end_date=end_date,
                payment_status=payment_status,
                price_paid=price,
            )
            self._refresh_index()
            self.activity_queue.enqueue(
                ActivityLog(
                    action_type="RENEW",
                    entity_name="Subscription",
                    entity_id=member_id,
                    description=f"Renewed {plan_name} subscription for member ID {member_id}",
                )
            )
            return True, "Subscription renewed successfully."
        except Exception as e:
            return False, f"Unable to renew subscription: {e}"

    # =========================================================================
    # Undo Functionality (Stack Operations)
    # =========================================================================

    def can_undo(self) -> bool:
        """Returns True if there is an action that can be undone."""
        return not self.undo_stack.is_empty()

    def get_last_undo_description(self) -> Optional[str]:
        """Returns description of the top undoable action."""
        top = self.undo_stack.peek()
        return top.description if top else None

    def undo_last_action(self) -> Tuple[bool, str]:
        """Pops and executes the most recent action from the Undo Stack."""
        action = self.undo_stack.pop()
        if not action:
            return False, "No action to undo."

        try:
            action.undo_callable()
            self.activity_queue.enqueue(
                ActivityLog(
                    action_type="UNDO",
                    entity_name="System",
                    entity_id=None,
                    description=f"Undid action: {action.description}",
                )
            )
            return True, f"Successfully undid: {action.description}"
        except Exception as e:
            return False, f"Failed to undo action '{action.description}': {e}"