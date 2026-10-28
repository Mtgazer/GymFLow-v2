#!/usr/bin/env python3
"""Database initialization script for GymFlow-v2.
Supports initializing either MySQL or SQLite with tables and default plan data.
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config as cfg


def init_mysql():
    """Initializes MySQL database using mysql-connector-python or pymysql."""
    print(f"Connecting to MySQL server at {cfg.DB_HOST}:{cfg.DB_PORT} as '{cfg.DB_USER}'...")
    
    conn = None
    try:
        # Try mysql.connector first
        import mysql.connector
        conn = mysql.connector.connect(
            host=cfg.DB_HOST,
            port=cfg.DB_PORT,
            user=cfg.DB_USER,
            password=cfg.DB_PASSWORD,
        )
    except Exception as e_connector:
        try:
            import pymysql
            conn = pymysql.connect(
                host=cfg.DB_HOST,
                port=cfg.DB_PORT,
                user=cfg.DB_USER,
                password=cfg.DB_PASSWORD,
            )
        except Exception as e_pymysql:
            print(f"[ERROR] Could not connect to MySQL server.")
            print(f"  mysql.connector error: {e_connector}")
            print(f"  pymysql error: {e_pymysql}")
            return False

    try:
        cursor = conn.cursor()
        print(f"Creating database '{cfg.DB_NAME}' if not exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {cfg.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute(f"USE {cfg.DB_NAME};")

        # Read schema.sql
        schema_path = PROJECT_ROOT / "database" / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Split statements by semicolon
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
        for stmt in statements:
            if stmt.lower().startswith("create database") or stmt.lower().startswith("use "):
                continue
            cursor.execute(stmt)

        conn.commit()
        cursor.close()
        conn.close()
        print("[SUCCESS] MySQL database and tables created and seeded successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed during MySQL schema execution: {e}")
        if conn:
            conn.close()
        return False


def init_sqlite(db_path=None):
    """Initializes local SQLite database and seeds default plans."""
    import sqlite3
    target_path = db_path or cfg.SQLITE_PATH
    print(f"Initializing SQLite database at '{target_path}'...")
    
    conn = sqlite3.connect(target_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            age INTEGER DEFAULT 0,
            gender TEXT DEFAULT 'Unknown',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            duration_days INTEGER NOT NULL,
            price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            payment_status TEXT NOT NULL CHECK (payment_status IN ('Paid', 'Pending', 'Cancelled')),
            price_paid REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
            FOREIGN KEY (plan_id) REFERENCES plans(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            entity_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed default plans
    plans = [
        ("Basic", 30, 250.0),
        ("Premium", 30, 350.0),
        ("Gold", 30, 500.0),
        ("VIP Annual", 365, 3500.0),
    ]
    for name, duration, price in plans:
        cursor.execute(
            "INSERT OR IGNORE INTO plans (name, duration_days, price) VALUES (?, ?, ?);",
            (name, duration, price)
        )

    conn.commit()
    conn.close()
    print("[SUCCESS] SQLite database initialized and seeded successfully!")
    return True


def main():
    print(f"=== GymFlow Database Initializer ===")
    print(f"Target DB Type: {cfg.DB_TYPE.upper()}")

    if cfg.DB_TYPE == "mysql":
        success = init_mysql()
        if not success:
            if cfg.SQLITE_FALLBACK:
                print("\n[INFO] MySQL connection failed. Falling back to SQLite setup...")
                init_sqlite()
            else:
                print("\n[FAILED] Could not initialize MySQL and fallback is disabled.")
                sys.exit(1)
    else:
        init_sqlite()


if __name__ == "__main__":
    main()
