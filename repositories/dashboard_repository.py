"""Dashboard Repository handling analytical and summary queries."""
from typing import Any, Dict, List, Optional

from data.connection import DatabaseConnectionManager


class DashboardRepository:
    """Repository dedicated to dashboard analytics and aggregation queries."""

    def __init__(self, db_manager: Optional[DatabaseConnectionManager] = None):
        self.db = db_manager or DatabaseConnectionManager()

    def get_total_members(self) -> int:
        """Counts total registered gym members."""
        query = "SELECT COUNT(*) FROM members;"
        val = self.db.execute_scalar(query)
        return int(val or 0)

    def get_active_members(self) -> int:
        """Counts distinct members with active (non-expired) subscriptions."""
        if self.db.is_mysql:
            query = """
                SELECT COUNT(DISTINCT member_id)
                FROM subscriptions
                WHERE end_date >= CURDATE();
            """
        else:
            query = """
                SELECT COUNT(DISTINCT member_id)
                FROM subscriptions
                WHERE end_date >= DATE('now');
            """
        val = self.db.execute_scalar(query)
        return int(val or 0)

    def get_expired_members(self) -> int:
        """Counts distinct members whose subscriptions have expired."""
        if self.db.is_mysql:
            query = """
                SELECT COUNT(DISTINCT member_id)
                FROM subscriptions
                WHERE end_date < CURDATE();
            """
        else:
            query = """
                SELECT COUNT(DISTINCT member_id)
                FROM subscriptions
                WHERE end_date < DATE('now');
            """
        val = self.db.execute_scalar(query)
        return int(val or 0)

    def get_total_revenue(self) -> float:
        """Computes total revenue collected from subscriptions."""
        query = "SELECT COALESCE(SUM(price_paid), 0) FROM subscriptions;"
        val = self.db.execute_scalar(query)
        return float(val or 0.0)

    def get_recent_subscriptions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves most recent subscriptions for activity feed."""
        query = f"""
            SELECT
                members.full_name,
                plans.name AS plan_name,
                subscriptions.payment_status,
                subscriptions.end_date
            FROM subscriptions
            JOIN members ON subscriptions.member_id = members.id
            JOIN plans ON subscriptions.plan_id = plans.id
            ORDER BY subscriptions.id DESC
            LIMIT {limit};
        """
        return self.db.execute_query(query)
