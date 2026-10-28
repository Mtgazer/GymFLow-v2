"""Member Repository implementing Member and Subscription data access."""
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from data.connection import DatabaseConnectionManager
from models import Member, Subscription
from repositories.base_repository import BaseRepository


class MemberRepository(BaseRepository[Member]):
    """Repository handling CRUD operations and data queries for Members and Subscriptions.
    Demonstrates the GoF Repository Pattern, decoupling services from raw SQL.
    """

    def __init__(self, db_manager: Optional[DatabaseConnectionManager] = None):
        self.db = db_manager or DatabaseConnectionManager()

    def add(self, entity: Member) -> int:
        """Inserts a new member record. Returns generated member ID."""
        query = """
            INSERT INTO members (full_name, phone, age, gender)
            VALUES (?, ?, ?, ?);
        """
        return self.db.execute_non_query(
            query, (entity.full_name, entity.phone, entity.age, entity.gender)
        )

    def get_by_id(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves member record joined with latest subscription and plan info."""
        query = """
            SELECT
                members.*,
                subscriptions.id AS subscription_id,
                subscriptions.plan_id,
                subscriptions.price_paid,
                subscriptions.start_date,
                subscriptions.end_date,
                subscriptions.payment_status,
                plans.name AS plan_name
            FROM members
            LEFT JOIN subscriptions
                ON members.id = subscriptions.member_id
            LEFT JOIN plans
                ON subscriptions.plan_id = plans.id
            WHERE members.id = ?
            ORDER BY subscriptions.id DESC
            LIMIT 1;
        """
        return self.db.execute_one(query, (entity_id,))

    def get_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Retrieves raw member record by unique phone number."""
        query = "SELECT * FROM members WHERE phone = ?;"
        return self.db.execute_one(query, (phone.strip(),))

    def get_all(self) -> List[Member]:
        """Retrieves all members as domain objects."""
        query = "SELECT * FROM members ORDER BY full_name ASC;"
        rows = self.db.execute_query(query)
        return [Member.from_db(row) for row in rows]

    def get_members_display(self) -> List[Member]:
        """Retrieves all members with their latest plan and expiry date for GUI listing."""
        query = """
            SELECT
                members.id,
                members.full_name,
                members.phone,
                members.age,
                members.gender,
                members.created_at,
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
        rows = self.db.execute_query(query)
        return [Member.from_db(row) for row in rows]

    def update(self, entity: Member) -> bool:
        """Updates basic demographic details of a member."""
        if entity.id is None:
            return False
        query = """
            UPDATE members
            SET full_name = ?, phone = ?, age = ?, gender = ?
            WHERE id = ?;
        """
        rows_affected = self.db.execute_non_query(
            query, (entity.full_name, entity.phone, entity.age, entity.gender, entity.id)
        )
        return rows_affected > 0

    def update_member_and_subscription(
        self,
        member_id: int,
        full_name: str,
        phone: str,
        plan_id: int,
        price_paid: float,
    ) -> bool:
        """Updates member profile and their latest subscription in one operation."""
        # 1. Update member profile
        update_member_sql = """
            UPDATE members
            SET full_name = ?, phone = ?
            WHERE id = ?;
        """
        self.db.execute_non_query(update_member_sql, (full_name, phone, member_id))

        # 2. Update latest subscription if one exists
        update_sub_sql = """
            UPDATE subscriptions
            SET plan_id = ?, price_paid = ?
            WHERE id = (
                SELECT sub_id FROM (
                    SELECT id AS sub_id
                    FROM subscriptions
                    WHERE member_id = ?
                    ORDER BY id DESC
                    LIMIT 1
                ) AS temp
            );
        """
        # For SQLite and MySQL cross-compatibility
        try:
            self.db.execute_non_query(update_sub_sql, (plan_id, price_paid, member_id))
        except Exception:
            # Fallback for simpler subquery
            direct_sql = """
                UPDATE subscriptions
                SET plan_id = ?, price_paid = ?
                WHERE member_id = ?;
            """
            self.db.execute_non_query(direct_sql, (plan_id, price_paid, member_id))

        return True

    def delete(self, entity_id: int) -> bool:
        """Deletes a member and all their subscriptions."""
        # Clean subscriptions first to ensure integrity
        del_subs_sql = "DELETE FROM subscriptions WHERE member_id = ?;"
        self.db.execute_non_query(del_subs_sql, (entity_id,))

        del_member_sql = "DELETE FROM members WHERE id = ?;"
        rows_affected = self.db.execute_non_query(del_member_sql, (entity_id,))
        return rows_affected > 0

    def create_subscription(
        self,
        member_id: int,
        plan_id: int,
        start_date: date,
        end_date: date,
        payment_status: str,
        price_paid: float,
    ) -> int:
        """Inserts a new subscription record."""
        query = """
            INSERT INTO subscriptions (
                member_id, plan_id, start_date, end_date, payment_status, price_paid
            )
            VALUES (?, ?, ?, ?, ?, ?);
        """
        return self.db.execute_non_query(
            query,
            (
                member_id,
                plan_id,
                str(start_date),
                str(end_date),
                payment_status,
                price_paid,
            ),
        )

    def restore_member_with_subscription(
        self,
        member_data: Dict[str, Any],
        subscription_data: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Restores a deleted member and their subscription for Undo functionality."""
        query = """
            INSERT INTO members (id, full_name, phone, age, gender, created_at)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        self.db.execute_non_query(
            query,
            (
                member_data.get("id"),
                member_data.get("full_name"),
                member_data.get("phone"),
                member_data.get("age", 0),
                member_data.get("gender", "Unknown"),
                member_data.get("created_at"),
            ),
        )
        new_id = member_data.get("id")

        if subscription_data and new_id:
            sub_query = """
                INSERT INTO subscriptions (
                    member_id, plan_id, start_date, end_date, payment_status, price_paid
                )
                VALUES (?, ?, ?, ?, ?, ?);
            """
            self.db.execute_non_query(
                sub_query,
                (
                    new_id,
                    subscription_data.get("plan_id"),
                    subscription_data.get("start_date"),
                    subscription_data.get("end_date"),
                    subscription_data.get("payment_status", "Paid"),
                    subscription_data.get("price_paid", 0.0),
                ),
            )
        return new_id
