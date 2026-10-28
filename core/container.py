"""Dependency Injection Container for GymFlow-v2.
Wires up the Singleton DatabaseConnectionManager, Repositories, and Services
according to Layered Architecture.
"""
from typing import Optional

from data.connection import DatabaseConnectionManager
from data.database import Database
from repositories.dashboard_repository import DashboardRepository
from repositories.member_repository import MemberRepository
from repositories.plan_repository import PlanRepository
from services.dashboard_service import DashboardService
from services.member_service import MemberService


class Container:
    """Application Dependency Injection Container.
    Initializes and holds singleton instances of data access, repositories, and services.
    """

    def __init__(self, force_sqlite: bool = False, db_path: Optional[str] = None):
        # 1. Data Connection Manager (Singleton)
        self.db_manager = DatabaseConnectionManager(
            force_sqlite=force_sqlite, db_path=db_path
        )

        # 2. Compatibility Database Facade
        self.database = Database(db_path=db_path)

        # 3. Data Access Layer / Repositories (Repository Pattern)
        self.member_repo = MemberRepository(self.db_manager)
        self.plan_repo = PlanRepository(self.db_manager)
        self.dashboard_repo = DashboardRepository(self.db_manager)

        # 4. Business Logic Layer / Services
        self.member_service = MemberService(
            database=self.database,
            member_repo=self.member_repo,
            plan_repo=self.plan_repo,
        )
        self.dashboard_service = DashboardService(
            database=self.database,
            dashboard_repo=self.dashboard_repo,
        )
