"""Unit tests verifying Software Engineering Design Patterns and Architecture:
- GoF Singleton Pattern (DatabaseConnectionManager)
- GoF Repository Pattern (BaseRepository, MemberRepository, PlanRepository)
- Layered Architecture separation
- MySQL Connection abstraction and fallback
"""
import concurrent.futures
import pytest
from unittest.mock import MagicMock, patch
from data.connection import DatabaseConnectionManager
from models import Member, Plan
from repositories.base_repository import BaseRepository
from repositories.member_repository import MemberRepository
from repositories.plan_repository import PlanRepository


class TestDesignPatterns:

    # =========================================================================
    # 1. Singleton Pattern
    # =========================================================================

    def test_singleton_identity(self):
        """Verifies that DatabaseConnectionManager returns the identical instance."""
        DatabaseConnectionManager.reset_instance_for_testing()

        instance_a = DatabaseConnectionManager(force_sqlite=True, db_path=":memory:")
        instance_b = DatabaseConnectionManager(force_sqlite=True, db_path=":memory:")

        assert instance_a is instance_b
        assert id(instance_a) == id(instance_b)

        instance_a.close()
        DatabaseConnectionManager.reset_instance_for_testing()

    def test_singleton_thread_safety(self):
        """Verifies thread-safe singleton initialization under concurrent access."""
        DatabaseConnectionManager.reset_instance_for_testing()

        instances = []

        def get_instance():
            return DatabaseConnectionManager(force_sqlite=True, db_path=":memory:")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_instance) for _ in range(20)]
            for f in concurrent.futures.as_completed(futures):
                instances.append(f.result())

        # All 20 threads must have received the exact same instance
        first_instance = instances[0]
        assert all(inst is first_instance for inst in instances)

        first_instance.close()
        DatabaseConnectionManager.reset_instance_for_testing()

    # =========================================================================
    # 2. Repository Pattern
    # =========================================================================

    def test_repository_pattern_conformance(self):
        """Verifies that repositories implement the abstract BaseRepository interface."""
        assert issubclass(MemberRepository, BaseRepository)
        assert issubclass(PlanRepository, BaseRepository)

        # Check required CRUD methods are present on BaseRepository
        required_methods = ["add", "get_by_id", "get_all", "update", "delete"]
        for method_name in required_methods:
            assert hasattr(BaseRepository, method_name)
            assert getattr(BaseRepository, method_name).__isabstractmethod__ is True

    # =========================================================================
    # 3. Layered Architecture Separation
    # =========================================================================

    def test_layered_architecture_isolation(self):
        """Verifies that UI layer components do not import SQL or database modules directly."""
        import ui.dialogs.add_member as add_dialog
        import ui.dialogs.edit_member as edit_dialog
        import ui.dialogs.renew_member as renew_dialog
        import ui.members as members_ui

        # UI modules must only communicate with the service layer
        for mod in [add_dialog, edit_dialog, renew_dialog, members_ui]:
            mod_vars = dir(mod)
            assert "sqlite3" not in mod_vars
            assert "mysql" not in mod_vars
            assert "DatabaseConnectionManager" not in mod_vars

    # =========================================================================
    # 4. MySQL Connection Abstraction and Fallback
    # =========================================================================

    def test_mysql_connection_mock(self):
        """Tests that when MySQL connection succeeds, driver is set to 'mysql'."""
        DatabaseConnectionManager.reset_instance_for_testing()

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch("config.DB_TYPE", "mysql"):
            with patch("mysql.connector.connect", return_value=mock_conn):
                manager = DatabaseConnectionManager()
                assert manager.is_mysql is True
                assert manager.driver == "mysql"
                manager.close()

        DatabaseConnectionManager.reset_instance_for_testing()

    def test_mysql_fallback_to_sqlite(self):
        """Tests that when MySQL fails and SQLITE_FALLBACK is True, it falls back to SQLite."""
        DatabaseConnectionManager.reset_instance_for_testing()

        with patch("config.DB_TYPE", "mysql"):
            with patch("config.SQLITE_FALLBACK", True):
                with patch("mysql.connector.connect", side_effect=Exception("Connection refused")):
                    with patch("pymysql.connect", side_effect=Exception("Connection refused")):
                        manager = DatabaseConnectionManager()
                        assert manager.is_mysql is False
                        assert manager.driver == "sqlite"
                        manager.close()

        DatabaseConnectionManager.reset_instance_for_testing()
