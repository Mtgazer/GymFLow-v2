"""Integration unit tests for Data Access Layer / Repositories.
Uses an isolated SQLite test database to ensure tests never touch live user data.
"""
import pytest
from datetime import date, timedelta
from data.connection import DatabaseConnectionManager
from database.init_db import init_sqlite
from models import Member, Plan
from repositories.dashboard_repository import DashboardRepository
from repositories.member_repository import MemberRepository
from repositories.plan_repository import PlanRepository


@pytest.fixture
def test_db_manager(tmp_path):
    """Fixture initializing an isolated temporary database for testing."""
    test_db_file = str(tmp_path / "test_gym.db")
    init_sqlite(test_db_file)

    DatabaseConnectionManager.reset_instance_for_testing()
    manager = DatabaseConnectionManager(force_sqlite=True, db_path=test_db_file)
    yield manager
    manager.close()
    DatabaseConnectionManager.reset_instance_for_testing()


class TestRepositories:

    def test_plan_repository_crud(self, test_db_manager):
        """Tests full CRUD lifecycle for PlanRepository."""
        repo = PlanRepository(test_db_manager)

        # 1. Read seeded plans
        plans = repo.get_all()
        assert len(plans) >= 3
        plan_names = [p.name for p in plans]
        assert "Basic" in plan_names
        assert "Gold" in plan_names

        # 2. Get by name & ID
        gold = repo.get_by_name("Gold")
        assert gold is not None
        assert gold.price == 500.0

        gold_by_id = repo.get_by_id(gold.id)
        assert gold_by_id.name == "Gold"

        # 3. Create new plan
        custom_plan = Plan(name="Student Special", duration_days=45, price=180.0)
        new_id = repo.add(custom_plan)
        assert new_id > 0

        created = repo.get_by_id(new_id)
        assert created.name == "Student Special"
        assert created.duration_days == 45
        assert created.price == 180.0

        # 4. Update plan
        created.price = 195.0
        success = repo.update(created)
        assert success is True
        assert repo.get_by_id(new_id).price == 195.0

        # 5. Delete plan
        deleted = repo.delete(new_id)
        assert deleted is True
        assert repo.get_by_id(new_id) is None

    def test_member_repository_crud_and_subscriptions(self, test_db_manager):
        """Tests full CRUD lifecycle for MemberRepository and subscription linking."""
        member_repo = MemberRepository(test_db_manager)
        plan_repo = PlanRepository(test_db_manager)

        basic_plan = plan_repo.get_by_name("Basic")
        assert basic_plan is not None

        # 1. Create Member
        member = Member(
            full_name="Mahmoud Gamal",
            phone="01099887766",
            age=28,
            gender="Male",
        )
        member_id = member_repo.add(member)
        assert member_id > 0

        # 2. Create Subscription
        today = date.today()
        expiry = today + timedelta(days=30)
        sub_id = member_repo.create_subscription(
            member_id=member_id,
            plan_id=basic_plan.id,
            start_date=today,
            end_date=expiry,
            payment_status="Paid",
            price_paid=250.0,
        )
        assert sub_id > 0

        # 3. Read Member by ID & Phone
        fetched = member_repo.get_by_id(member_id)
        assert fetched is not None
        assert fetched["full_name"] == "Mahmoud Gamal"
        assert fetched["plan_name"] == "Basic"
        assert fetched["price_paid"] == 250.0

        by_phone = member_repo.get_by_phone("01099887766")
        assert by_phone is not None
        assert by_phone["id"] == member_id

        # 4. Read Display Members
        display_members = member_repo.get_members_display()
        assert len(display_members) >= 1
        m_display = next(m for m in display_members if m.id == member_id)
        assert m_display.full_name == "Mahmoud Gamal"
        assert m_display.plan == "Basic"
        assert m_display.expiry == str(expiry)

        # 5. Update Member Profile and Subscription
        premium_plan = plan_repo.get_by_name("Premium")
        upd_success = member_repo.update_member_and_subscription(
            member_id=member_id,
            full_name="Mahmoud G. Hassan",
            phone="01099887799",
            plan_id=premium_plan.id,
            price_paid=350.0,
        )
        assert upd_success is True

        updated = member_repo.get_by_id(member_id)
        assert updated["full_name"] == "Mahmoud G. Hassan"
        assert updated["phone"] == "01099887799"
        assert updated["plan_name"] == "Premium"
        assert updated["price_paid"] == 350.0

        # 6. Delete Member and Subscriptions
        del_success = member_repo.delete(member_id)
        assert del_success is True
        assert member_repo.get_by_id(member_id) is None

        # 7. Restore Member (Undo support)
        restored_id = member_repo.restore_member_with_subscription(
            member_data=updated,
            subscription_data=updated,
        )
        assert restored_id == member_id
        restored = member_repo.get_by_id(member_id)
        assert restored is not None
        assert restored["full_name"] == "Mahmoud G. Hassan"

    def test_dashboard_repository_metrics(self, test_db_manager):
        """Tests analytical aggregation queries in DashboardRepository."""
        member_repo = MemberRepository(test_db_manager)
        plan_repo = PlanRepository(test_db_manager)
        dash_repo = DashboardRepository(test_db_manager)

        plan = plan_repo.get_by_name("Gold")

        # Initial metrics
        initial_members = dash_repo.get_total_members()
        initial_revenue = dash_repo.get_total_revenue()

        # Add active member
        m1_id = member_repo.add(Member(full_name="Active User", phone="01111111111"))
        member_repo.create_subscription(
            member_id=m1_id,
            plan_id=plan.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            payment_status="Paid",
            price_paid=500.0,
        )

        # Add expired member
        m2_id = member_repo.add(Member(full_name="Expired User", phone="01222222222"))
        member_repo.create_subscription(
            member_id=m2_id,
            plan_id=plan.id,
            start_date=date.today() - timedelta(days=60),
            end_date=date.today() - timedelta(days=30),
            payment_status="Paid",
            price_paid=500.0,
        )

        assert dash_repo.get_total_members() == initial_members + 2
        assert dash_repo.get_active_members() >= 1
        assert dash_repo.get_expired_members() >= 1
        assert dash_repo.get_total_revenue() == initial_revenue + 1000.0

        recent = dash_repo.get_recent_subscriptions(limit=5)
        assert len(recent) >= 2
        names = [r["full_name"] for r in recent]
        assert "Active User" in names
        assert "Expired User" in names
