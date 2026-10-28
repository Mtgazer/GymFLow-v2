"""Database Connection Manager implementing the Singleton Pattern.
Manages connections to MySQL (primary) and SQLite (fallback / test).
Provides a uniform interface with dictionary-like row results and parameterized queries.
"""
import logging
import sqlite3
import threading
from typing import Any, List, Optional, Tuple, Union

import config as cfg

logger = logging.getLogger("GymFlow.Database")


class DatabaseConnectionManager:
    """Thread-safe Singleton class managing database connectivity.
    Demonstrates the Singleton Design Pattern.
    """

    _instance: Optional["DatabaseConnectionManager"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, force_sqlite: bool = False, db_path: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return

        self._force_sqlite = force_sqlite
        self._custom_db_path = db_path
        self._connection = None
        self._driver: str = "sqlite"  # 'mysql' or 'sqlite'
        self._connect()
        self._initialized = True

    @property
    def driver(self) -> str:
        """Returns the active driver name: 'mysql' or 'sqlite'."""
        return self._driver

    @property
    def is_mysql(self) -> bool:
        """Returns True if connected to MySQL."""
        return self._driver == "mysql"

    def _connect(self):
        """Attempts connection to MySQL if configured, otherwise falls back to SQLite."""
        if not self._force_sqlite and cfg.DB_TYPE == "mysql":
            success = self._try_connect_mysql()
            if success:
                return
            if not cfg.SQLITE_FALLBACK:
                raise ConnectionError("Failed to connect to MySQL database and SQLITE_FALLBACK is disabled.")
            logger.warning("MySQL connection unavailable; falling back to SQLite.")

        self._connect_sqlite()

    def _try_connect_mysql(self) -> bool:
        """Attempts connection to MySQL using mysql-connector-python or pymysql."""
        # 1. Try mysql.connector
        try:
            import mysql.connector
            self._connection = mysql.connector.connect(
                host=cfg.DB_HOST,
                port=cfg.DB_PORT,
                user=cfg.DB_USER,
                password=cfg.DB_PASSWORD,
                database=cfg.DB_NAME,
                autocommit=False,
            )
            self._driver = "mysql"
            logger.info("Connected to MySQL database via mysql.connector.")
            return True
        except Exception as e_mysql:
            logger.debug("mysql.connector failed: %s", e_mysql)

        # 2. Try pymysql
        try:
            import pymysql
            import pymysql.cursors
            self._connection = pymysql.connect(
                host=cfg.DB_HOST,
                port=cfg.DB_PORT,
                user=cfg.DB_USER,
                password=cfg.DB_PASSWORD,
                database=cfg.DB_NAME,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
            self._driver = "mysql"
            logger.info("Connected to MySQL database via pymysql.")
            return True
        except Exception as e_pymysql:
            logger.debug("pymysql failed: %s", e_pymysql)

        return False

    def _connect_sqlite(self):
        """Connects to local SQLite database with Row factory and foreign keys enabled."""
        path = self._custom_db_path or cfg.SQLITE_PATH
        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON;")
        self._driver = "sqlite"
        logger.info("Connected to SQLite database at: %s", path)

    def _format_query(self, query: str) -> str:
        """Translates placeholder format between MySQL (%s) and SQLite (?).
        Internal repositories use '?' or '%s'; this ensures consistency.
        """
        if self._driver == "sqlite":
            # Convert %s to ?
            return query.replace("%s", "?")
        else:
            # Convert ? to %s
            return query.replace("?", "%s")

    def execute_query(
        self, query: str, params: Union[Tuple, List] = ()
    ) -> List[dict]:
        """Executes a SELECT query and returns rows as dictionaries."""
        formatted = self._format_query(query)
        cursor = self._connection.cursor()
        try:
            cursor.execute(formatted, params)
            if self._driver == "sqlite":
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                # MySQL cursor handling
                if hasattr(cursor, "description") and cursor.description:
                    columns = [col[0] for col in cursor.description]
                    raw_rows = cursor.fetchall()
                    if raw_rows and isinstance(raw_rows[0], dict):
                        return raw_rows
                    return [dict(zip(columns, row)) for row in raw_rows]
                return []
        finally:
            cursor.close()

    def execute_one(
        self, query: str, params: Union[Tuple, List] = ()
    ) -> Optional[dict]:
        """Executes a SELECT query and returns the first row as a dictionary, or None."""
        rows = self.execute_query(query, params)
        return rows[0] if rows else None

    def execute_scalar(
        self, query: str, params: Union[Tuple, List] = ()
    ) -> Any:
        """Executes a scalar query (e.g. COUNT, SUM) and returns the single value."""
        formatted = self._format_query(query)
        cursor = self._connection.cursor()
        try:
            cursor.execute(formatted, params)
            row = cursor.fetchone()
            if not row:
                return 0
            if isinstance(row, dict):
                return list(row.values())[0]
            return row[0]
        finally:
            cursor.close()

    def execute_non_query(
        self, query: str, params: Union[Tuple, List] = ()
    ) -> int:
        """Executes INSERT, UPDATE, or DELETE and returns lastrowid or affected rows.
        Commits transaction automatically.
        """
        formatted = self._format_query(query)
        cursor = self._connection.cursor()
        try:
            cursor.execute(formatted, params)
            self._connection.commit()
            last_id = getattr(cursor, "lastrowid", None)
            row_count = getattr(cursor, "rowcount", 0)
            return last_id if last_id else row_count
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cursor.close()

    def commit(self):
        """Explicitly commits the current transaction."""
        if self._connection:
            self._connection.commit()

    def rollback(self):
        """Rolls back the current transaction."""
        if self._connection:
            self._connection.rollback()

    def close(self):
        """Closes the underlying database connection and resets the singleton instance."""
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            self._connection = None
        DatabaseConnectionManager._instance = None
        self._initialized = False

    @classmethod
    def reset_instance_for_testing(cls):
        """Helper for unit tests to reset the singleton state."""
        with cls._lock:
            if cls._instance and cls._instance._connection:
                try:
                    cls._instance._connection.close()
                except Exception:
                    pass
            cls._instance = None
