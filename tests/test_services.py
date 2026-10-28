"""Unit tests for Service Layer (MemberService and DashboardService)
including Undo workflows and input validation.
"""
import pytest
from datetime import date, timedelta
from data.connection import DatabaseConnectionManager
from database.init_db import init_sqlite
from repositories.dashboard_repository import DashboardRepository
from repositories.member_repository import MemberRepository
from repositories.plan_repository import PlanRepository
from services.dashboard_service import DashboardService
from services.member_service import MemberService


@pytest.fixture
def service_env(tmp_path):
    """Sets up an isolated test database, repositories, and services."""
    test_db_file = str(tmp_path / "service_test.db")
    init_sqlite(test_db_file)

    DatabaseConnectionManager.reset_instance_for_testing()
    db_manager = DatabaseConnectionManager(force_sqlite=True, db_path=test_db_file)

    member_repo = MemberRepository(db_manager)
    plan_repo = PlanRepository(db_manager)
    dash_repo = DashboardRepository(db_manager)

    member_service = MemberService(member_repo=member_repo, plan_repo=plan_repo)
    dash_service = DashboardService(dashboard_repo=dash_repo)

    yield member_service, dash_service, member_repo, plan_repo

    db_manager.close()
    DatabaseConnectionManager.reset_instance_for_testing()


class TestServices:

    def test_input_validation(self, service_env):
        """Tests input validation rules in MemberService."""
        member_service, _, _, _ = service_env

        # Valid input
        valid, msg = member_service.validate_member_input("Kareem Ali", "01012345678", 350.0)
        assert valid is True
        assert msg == ""

        # Short/empty name
        valid, msg = member_service.validate_member_input("A", "01012345678", 350.0)
        assert valid is False
        assert "at least 2 characters" in msg

        # Empty phone
        valid, msg = member_service.validate_member_input("Kareem Ali", "", 350.0)
        assert valid is False
        assert "Phone number is required" in msg

        # Invalid phone format
        valid, msg = member_service.validate_member_input("Kareem Ali", "abc", 350.0)
        assert valid is False
        assert "Invalid phone number format" in msg

        # Negative price
        valid, msg = member_service.validate_member_input("Kareem Ali", "01012345678", -50)
        assert valid is False
        assert "Price cannot be negative" in msg

        # Non-numeric price
        valid, msg = member_service.validate_member_input("Kareem Ali", "01012345678", "free")
        assert valid is False
        assert "valid number" in msg

    def test_register_member_and_undo(self, service_env):
        """Tests member registration, index caching, queue logging, and Undo reversal."""
        member_service, _, _, _ = service_env

        assert member_service.can_undo() is False

        # Register new member
        success, msg = member_service.register_member(
            full_name="Youssef Nabil",
            phone="01099881122",
            plan_name="Premium",
            price_paid=350.0,
        )
        assert success is True
        assert "registered successfully" in msg.lower()

        # Check lookup dictionary O(1)
        cached = member_service.lookup_index.get_by_phone("01099881122")
        assert cached is not None
        assert cached.full_name == "Youssef Nabil"
        member_id = cached.id

        # Check queue
        assert member_service.activity_queue.size() >= 1

        # Check undo stack
        assert member_service.can_undo() is True
        assert "Youssef Nabil" in member_service.get_last_undo_description()

        # Trigger Undo (LIFO)
        undo_success, undo_msg = member_service.undo_last_action()
        assert undo_success is True
        assert "Successfully undid" in undo_msg

        # Member should no longer exist
        assert member_service.lookup_index.get_by_phone("01099881122") is None
        assert member_service.get_member_by_id(member_id) is None
        assert member_service.can_undo() is False

    def test_duplicate_phone_prevention(self, service_env):
        """Tests rejection of duplicate phone numbers."""
        member_service, _, _, _ = service_env

        s1, _ = member_service.register_member(
            full_name="First Member",
            phone="01155443322",
            plan_name="Basic",
            price_paid=250.0,
        )
        assert s1 is True

        # Second registration with identical phone
        s2, err_msg = member_service.register_member(
            full_name="Duplicate Member",
            phone="01155443322",
            plan_name="Gold",
            price_paid=500.0,
        )
        assert s2 is False
        assert "already exists" in err_msg.lower()

    def test_edit_and_undo(self, service_env):
        """Tests editing a member profile and undoing the modification."""
        member_service, _, _, _ = service_env

        # Create member
        member_service.register_member(
            full_name="Original Name",
            phone="01077778888",
            plan_name="Basic",
            price_paid=250.0,
        )
        member = member_service.lookup_index.get_by_phone("01077778888")
        assert member is not None

        # Edit member
        edit_ok, _ = member_service.edit_member(
            member_id=member.id,
            full_name="Updated Name",
            phone="01077779999",
            plan_name="Gold",
            price_paid=500.0,
        )
        assert edit_ok is True

        # Verify update
        updated_data = member_service.get_member_by_id(member.id)
        assert updated_data["full_name"] == "Updated Name"
        assert updated_data["phone"] == "01077779999"
        assert updated_data["plan_name"] == "Gold"

        # Undo edit
        undo_ok, _ = member_service.undo_last_action()
        assert undo_ok is True

        reverted = member_service.get_member_by_id(member.id)
        assert reverted["full_name"] == "Original Name"
        assert reverted["phone"] == "01077778888"

    def test_delete_and_undo(self, service_env):
        """Tests deleting a member and fully restoring them via UndoStack."""
        member_service, _, _, _ = service_env

        member_service.register_member(
            full_name="To Delete",
            phone="01011110000",
            plan_name="Gold",
            price_paid=500.0,
        )
        member = member_service.lookup_index.get_by_phone("01011110000")
        member_id = member.id

        # Delete member
        del_ok = member_service.delete_member(member_id)
        assert del_ok is True
        assert member_service.get_member_by_id(member_id) is None

        # Undo deletion
        undo_ok, _ = member_service.undo_last_action()
        assert undo_ok is True

        restored = member_service.get_member_by_id(member_id)
        assert restored is not None
        assert restored["full_name"] == "To Delete"
        assert restored["phone"] == "01011110000"

    def test_renew_member(self, service_env):
        """Tests membership renewal logic."""
        member_service, _, _, _ = service_env

        member_service.register_member(
            full_name="Renewal Candidate",
            phone="01299998888",
            plan_name="Basic",
            price_paid=250.0,
        )
        member = member_service.lookup_index.get_by_phone("01299998888")

        renew_ok, renew_msg = member_service.renew_member(
            member_id=member.id,
            plan_name="VIP Annual",
            payment_status="Paid",
            price_paid=3500.0,
        )
        assert renew_ok is True
        assert "renewed successfully" in renew_msg.lower()

        updated = member_service.get_member_by_id(member.id)
        assert updated["plan_name"] == "VIP Annual"
        assert updated["price_paid"] == 3500.0

    def test_dashboard_service_summary(self, service_env):
        """Tests dashboard service analytical operations."""
        member_service, dash_service, _, _ = service_env

        member_service.register_member("User 1", "01010101010", "Basic", 250.0)
        member_service.register_member("User 2", "01020202020", "Gold", 500.0)

        assert dash_service.get_total_members() >= 2
        assert dash_service.get_active_members() >= 2
        assert dash_service.get_total_revenue() >= 750.0

        recent = dash_service.get_recent_subscriptions(limit=5)
        assert len(recent) >= 2
        assert any(r[0] == "User 2" for r in recent)
