from data.database import Database


class DashboardService:
    def __init__(self, database: Database):
        self.db = database

    def get_total_members(self):
        return self.db.get_total_members()

    def get_active_members(self):
        return self.db.get_active_members()

    def get_expired_members(self):
        return self.db.get_expired_members()

    def get_total_revenue(self):
        return self.db.get_total_revenue()

    def get_recent_subscriptions(self):
        rows = self.db.get_recent_subscriptions()

        subscriptions = []

        for row in rows:
            subscriptions.append(
                (
                    row["full_name"],
                    row["plan_name"],
                    row["payment_status"],
                    row["end_date"],
                )
            )

        return subscriptions