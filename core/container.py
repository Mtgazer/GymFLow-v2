from data.database import Database
from services.member_service import MemberService
from services.dashboard_service import DashboardService

class Container:
    def __init__(self):
        # Shared database instance
        self.database = Database()

        # Services
        self.member_service = MemberService(self.database)
        self.dashboard_service = DashboardService(self.database)
