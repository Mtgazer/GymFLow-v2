"""Data Access Layer Compatibility Facade.
Wraps the DatabaseConnectionManager Singleton and repositories to maintain
backward compatibility with any existing calls while utilizing the new
Repository Pattern and MySQL/SQLite unified driver.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from data.connection import DatabaseConnectionManager
from models import Member, Plan
from repositories.dashboard_repository import DashboardRepository
from repositories.member_repository import MemberRepository
from repositories.plan_repository import PlanRepository


class Database:
    """Compatibility facade bridging legacy calls to the new Repository Pattern
    and DatabaseConnectionManager.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.connection_manager = DatabaseConnectionManager(db_path=db_path)
        self.member_repo = MemberRepository(self.connection_manager)
        self.plan_repo = PlanRepository(self.connection_manager)
        self.dashboard_repo = DashboardRepository(self.connection_manager)
        print("Database initialized successfully!")

    @property
    def connection(self):
        return self.connection_manager._connection

    @property
    def cursor(self):
        return self.connection.cursor()

    def create_tables(self):
        """Tables are managed by database/init_db.py or connection manager."""
        pass

    def add_member(
        self, full_name: str, phone: str, age: int = 0, gender: str = "Unknown"
    ) -> Tuple[bool, Union[int, str]]:
        try:
            member = Member(
                full_name=full_name, phone=phone, age=age, gender=gender
            )
            member_id = self.member_repo.add(member)
            return True, member_id
        except Exception as e:
            err_msg = str(e).lower()
            if "unique" in err_msg or "duplicate" in err_msg:
                return False, "Phone number already exists."
            return False, f"Failed to add member: {e}"

    def get_member_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        return self.member_repo.get_by_phone(phone)

    def get_all_members(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM members ORDER BY full_name ASC;"
        return self.connection_manager.execute_query(query)

    def get_plan_by_id(self, plan_id: int) -> Optional[Dict[str, Any]]:
        plan = self.plan_repo.get_by_id(plan_id)
        return plan.to_dict() if plan else None

    def get_plan_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        plan = self.plan_repo.get_by_name(name)
        return plan.to_dict() if plan else None

    def create_subscription(
        self,
        member_id: int,
        plan_id: int,
        payment_status: str,
        price_paid: float,
    ) -> Tuple[bool, str]:
        plan = self.plan_repo.get_by_id(plan_id)
        if plan is None:
            return False, "Plan not found."

        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=plan.duration_days)

        try:
            self.member_repo.create_subscription(
                member_id=member_id,
                plan_id=plan_id,
                start_date=start_date,
                end_date=end_date,
                payment_status=payment_status,
                price_paid=price_paid,
            )
            return True, "Subscription created successfully!"
        except Exception as e:
            return False, f"Unable to create subscription: {e}"

    def add_plan(
        self, name: str, duration_days: int, price: float
    ) -> Tuple[bool, str]:
        try:
            plan = Plan(name=name, duration_days=duration_days, price=price)
            self.plan_repo.add(plan)
            return True, "Plan added successfully."
        except Exception as e:
            return False, str(e)

    def delete_member(self, member_id: int) -> bool:
        try:
            return self.member_repo.delete(member_id)
        except Exception:
            return False

    def update_member(
        self,
        member_id: int,
        full_name: str,
        phone: str,
        plan_id: int,
        price_paid: float,
    ) -> bool:
        try:
            return self.member_repo.update_member_and_subscription(
                member_id=member_id,
                full_name=full_name,
                phone=phone,
                plan_id=plan_id,
                price_paid=price_paid,
            )
        except Exception as e:
            print(f"Error updating member: {e}")
            return False

    def get_member_by_id(self, member_id: int) -> Optional[Dict[str, Any]]:
        return self.member_repo.get_by_id(member_id)

    def get_total_members(self) -> int:
        return self.dashboard_repo.get_total_members()

    def get_active_members(self) -> int:
        return self.dashboard_repo.get_active_members()

    def get_expired_members(self) -> int:
        return self.dashboard_repo.get_expired_members()

    def get_total_revenue(self) -> float:
        return self.dashboard_repo.get_total_revenue()

    def get_recent_subscriptions(self) -> List[Dict[str, Any]]:
        return self.dashboard_repo.get_recent_subscriptions(limit=5)

    def get_members(self) -> List[Dict[str, Any]]:
        query = """
            SELECT
                members.id,
                members.full_name,
                members.phone,
                COALESCE(plans.name, '-') AS plan,
                COALESCE(subscriptions.end_date, '-') AS expiry
            FROM members
            LEFT JOIN subscriptions
                ON members.id = subscriptions.member_id
                AND subscriptions.id = (
                    SELECT s2.id
                    FROM subscriptions s2
                    WHERE s2.member_id = members.id
                    ORDER BY s2.id DESC
                    LIMIT 1
                )
            LEFT JOIN plans
                ON subscriptions.plan_id = plans.id
            ORDER BY members.full_name ASC;
        """
        return self.connection_manager.execute_query(query)