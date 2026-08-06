import sqlite3 
from datetime import datetime, timedelta
class Database:
    def __init__(self, db_path="gym.db"):
        self.connection = sqlite3.connect(db_path)

        self.connection.row_factory = sqlite3.Row

        # Enable foreign key enforcement
        self.connection.execute("PRAGMA foreign_keys = ON")

        self.cursor = self.connection.cursor()

        self.create_tables()

        print("Database initialized successfully!")


    def create_tables(self):
        self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
                            
        id INTEGER PRIMARY KEY AUTOINCREMENT,
                            
        full_name TEXT NOT NULL,
                            
        phone text UNIQUE NOT NULL,
                            
        age INTEGER,
                            
        gender TEXT,
                            
        created_at TIMESTAMP DEFAULT current_timestamp);
                            
    """)
        self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS plans (
                            
        id INTEGER PRIMARY KEY AUTOINCREMENT,
                            
        name TEXT NOT NULL,
                            
        duration_days INTEGER NOT NULL,
                            
        price REAL NOT NULL);
                            
    """)
        self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        member_id INTEGER NOT NULL,

        plan_id INTEGER NOT NULL,

        start_date DATE NOT NULL,

        end_date DATE NOT NULL,

        payment_status TEXT NOT NULL
            CHECK (
                payment_status IN (
                    'Paid',
                    'Pending',
                    'Cancelled'
            )
        ),

        price_paid REAL NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(member_id) REFERENCES members(id),

        FOREIGN KEY(plan_id) REFERENCES plans(id)

    );
    """)
        self.connection.commit()
    def add_member(self, full_name, phone, age, gender):
        try:

            self.cursor.execute(
                """
            insert into members(
                full_name,
                phone, 
                age, 
                gender
            )
            values(?, ?, ?, ?);
        """, (
                full_name,
                phone,
                age,
                gender
            )
            )   
            self.connection.commit()
        except sqlite3.IntegrityError:
            return False, "Phone number already exists."
        member_id = self.cursor.lastrowid
        return True, member_id
    def get_member_by_phone(self, phone):
        self.cursor.execute(
            """
                select * from members
                where phone = ?
            """, 
            (phone,)
            )

        return self.cursor.fetchone()
    def get_all_members(self):
        self.cursor.execute(
        """
            select * from members 
        """
        )
        return self.cursor.fetchall()
    def get_plan_by_id(self, plan_id):
        self.cursor.execute(
        """
            select * from plans where id = ?
        """, (plan_id, )
        )
        return self.cursor.fetchone()
    def get_plan_by_name(self, name):
        self.cursor.execute(
            """
            SELECT * 
            FROM plans
            where name = ?
            """,
            (name,)
        )
        return self.cursor.fetchone()
    def create_subscription(
        self,
        member_id,
        plan_id,
        payment_status,
        price_paid
    ):

        plan = self.get_plan_by_id(plan_id)

        if plan is None:
            return False, "Plan not found."

        duration_days = plan["duration_days"]

        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=duration_days)

        try:
            self.cursor.execute(
                """
                INSERT INTO subscriptions (
                    member_id,
                    plan_id,
                    start_date,
                    end_date,
                    payment_status,
                    price_paid
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    member_id,
                    plan_id,
                    start_date,
                    end_date,
                    payment_status,
                    price_paid
                )
            )

            self.connection.commit()

            return True, "Subscription created successfully!"

        except sqlite3.IntegrityError:
            return False, "Unable to create subscription."
    def add_plan(self,
                name,
                duration_days,
                price):
        try: 
            self.cursor.execute(
            """
            insert into plans 
            (
            name,
            duration_days,
            price
            )
            values(? ,? ,? )      
            """,
            (
            name,
            duration_days,
            price
            )

        )
            self.connection.commit()
            return True, "Plan added successfully."
        except sqlite3.Error as e:
            return False, str(e)
    def delete_member(self, member_id):

        try:

            self.cursor.execute(
                """
                DELETE FROM subscriptions
                WHERE member_id = ?
                """,
                (member_id,)
            )

            self.cursor.execute(
                """
                DELETE FROM members
                WHERE id = ?
                """,
                (member_id,)
            )

            self.connection.commit()

            return True

        except sqlite3.Error:
            return False
    def update_member(
        self,
        member_id,
        full_name,
        phone,
        plan_id,
        price_paid
    ):

        try:
            
            self.cursor.execute(
                """
                UPDATE members
                SET
                    full_name = ?,
                    phone = ?
                WHERE id = ?
                """,
                (
                    full_name,
                    phone,
                    member_id,
                )
            )

            self.cursor.execute(
                """
                UPDATE subscriptions
                SET
                    plan_id = ?,
                    price_paid = ?
                WHERE id = (
                    SELECT id
                    FROM subscriptions
                    WHERE member_id = ?
                    ORDER BY id DESC
                    LIMIT 1
                )
                """,
                (
                    plan_id,
                    price_paid,
                    member_id
                )
            )
            self.connection.commit()

            return True

        except sqlite3.Error as e:
            print(e)
            return False
    def get_member_by_id(self, member_id):

        self.cursor.execute(
            """
            SELECT
            members.*,
            subscriptions.plan_id,
            subscriptions.price_paid,
            plans.name AS plan_name
            FROM members
            LEFT JOIN subscriptions
                ON members.id = subscriptions.member_id
            LEFT JOIN plans
                ON subscriptions.plan_id = plans.id
            WHERE members.id = ?
            ORDER BY subscriptions.id DESC
            LIMIT 1;
            """,
            (member_id,)
        )

        return self.cursor.fetchone()
    
    def get_total_members(self):

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM members
        """)

        return self.cursor.fetchone()[0]
    
    def get_active_members(self):

        self.cursor.execute("""
            SELECT COUNT(DISTINCT member_id)
            FROM subscriptions
            WHERE end_date >= DATE('now')
        """)

        return self.cursor.fetchone()[0]
    def get_expired_members(self):

        self.cursor.execute("""
            SELECT COUNT(DISTINCT member_id)
            FROM subscriptions
            WHERE end_date < DATE('now')
        """)

        return self.cursor.fetchone()[0]
    
    def get_total_revenue(self):

        self.cursor.execute("""
            SELECT IFNULL(SUM(price_paid),0)
            FROM subscriptions
        """)

        return self.cursor.fetchone()[0]

    def get_recent_subscriptions(self):

        self.cursor.execute("""
            SELECT
                members.full_name,
                plans.name AS plan_name,
                subscriptions.payment_status,
                subscriptions.end_date
            FROM subscriptions
            JOIN members
                ON subscriptions.member_id = members.id
            JOIN plans
                ON subscriptions.plan_id = plans.id
            ORDER BY subscriptions.id DESC
            LIMIT 5
        """)

        return self.cursor.fetchall()

    def get_members(self):
        self.cursor.execute("""
            SELECT
                members.id,
                members.full_name,
                members.phone,
                COALESCE(plans.name, '-') AS plan,
                COALESCE(subscriptions.end_date, '-') AS expiry
            FROM members
            LEFT JOIN subscriptions
                ON members.id = subscriptions.member_id
                AND subscriptions.id = (
                    SELECT id
                    FROM subscriptions s2
                    WHERE s2.member_id = members.id
                    ORDER BY id DESC
                    LIMIT 1
                )
            LEFT JOIN plans
                ON subscriptions.plan_id = plans.id
            ORDER BY members.full_name;
        """)

        return self.cursor.fetchall()