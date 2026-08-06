from data.database import Database
from models import Member


class MemberService:
    def __init__(self, database: Database):
        self.db = database

    def add_member(self, member:Member):
        return self.db.add_member(
            member.full_name,
            member.phone,
            member.age,
            member.gender
        )

    def get_member_by_id(self, member_id : int):
        return self.db.get_member_by_id(member_id)

    def get_member_by_phone(self, phone: str):
        return self.db.get_member_by_phone(phone)

    def get_all_members(self):
        return self.db.get_all_members

    def update_member(
            self, 
            member_id,
            full_name,
            phone,
            plan_id,
            price_paid
        ):
        return self.db.update_member(
            member_id,
            full_name,
            phone,
            plan_id,
            price_paid
        )

    def delete_member(self, member_id):
        return self.db.delete_member(member_id)

    def get_members(self):
        rows = self.db.get_members()

        return [Member.from_db(row) for row in rows]

    def register_member(
    self,
    full_name: str,
    phone: str,
    plan_name: str,
    price_paid: float,
    ):
        # Create member
        success, result = self.db.add_member(
            full_name=full_name,
            phone=phone,
            age=0,
            gender="Unknown",
        )

        if not success:
            return False, result

        member_id = result

        # Get selected plan
        plan = self.db.get_plan_by_name(plan_name)

        if plan is None:
            return False, "Plan not found."

        # Create subscription
        success, message = self.db.create_subscription(
            member_id=member_id,
            plan_id=plan["id"],
            payment_status="Paid",
            price_paid=price_paid,
        )

        if not success:
            return False, message

        return True, "Member registered successfully."

    def edit_member(
        self,
        member_id,
        full_name,
        phone,
        plan_name,
        price_paid
    ):
        plan = self.db.get_plan_by_name(plan_name)

        if plan is None:
            return False, "Plan not found."

        success = self.db.update_member(
            member_id,
            full_name,
            phone,
            plan["id"],
            price_paid
        )

        if not success:
            return False, "Unable to update member."

        return True, "Member updated successfully."

    def renew_member(
        self,
        member_id,
        plan_name,
        payment_status,
        price_paid
    ):
        plan = self.db.get_plan_by_name(plan_name)

        if plan is None:
            return False, "Plan not found."

        return self.db.create_subscription(
            member_id=member_id,
            plan_id=plan["id"],
            payment_status=payment_status,
            price_paid=price_paid
        )