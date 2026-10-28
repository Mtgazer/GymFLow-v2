"""Dashboard Service providing business analytics and metrics."""
from typing import Any, List, Optional, Tuple

from data.database import Database
from repositories.dashboard_repository import DashboardRepository


class DashboardService:
    """Service layer for aggregating dashboard metrics and subscription summaries.
    Demonstrates Layered Architecture.
    """

    def __init__(
        self,
        database: Optional[Database] = None,
        dashboard_repo: Optional[DashboardRepository] = None,
    ):
        self.db = database or Database()
        self.repo = dashboard_repo or self.db.dashboard_repo

    def get_total_members(self) -> int:
        """Returns the total number of registered gym members."""
        return self.repo.get_total_members()

    def get_active_members(self) -> int:
        """Returns the count of members with currently active subscriptions."""
        return self.repo.get_active_members()

    def get_expired_members(self) -> int:
        """Returns the count of members with expired subscriptions."""
        return self.repo.get_expired_members()

    def get_total_revenue(self) -> float:
        """Returns the aggregate gross revenue collected from subscriptions."""
        return self.repo.get_total_revenue()

    def get_recent_subscriptions(self, limit: int = 5) -> List[Tuple[str, str, str, str]]:
        """Returns recent subscription records formatted for UI consumption."""
        rows = self.repo.get_recent_subscriptions(limit=limit)
        subscriptions = []
        for row in rows:
            subscriptions.append(
                (
                    str(row["full_name"]),
                    str(row["plan_name"]),
                    str(row["payment_status"]),
                    str(row["end_date"]),
                )
            )
        return subscriptions