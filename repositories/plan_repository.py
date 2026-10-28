"""Plan Repository implementing Plan entity data access."""
from typing import List, Optional

from data.connection import DatabaseConnectionManager
from models import Plan
from repositories.base_repository import BaseRepository


class PlanRepository(BaseRepository[Plan]):
    """Concrete repository for Gym Membership Plans.
    Demonstrates the Repository Pattern and Polymorphism.
    """

    def __init__(self, db_manager: Optional[DatabaseConnectionManager] = None):
        self.db = db_manager or DatabaseConnectionManager()

    def add(self, entity: Plan) -> int:
        query = """
            INSERT INTO plans (name, duration_days, price)
            VALUES (?, ?, ?);
        """
        return self.db.execute_non_query(
            query, (entity.name, entity.duration_days, entity.price)
        )

    def get_by_id(self, entity_id: int) -> Optional[Plan]:
        query = "SELECT * FROM plans WHERE id = ?;"
        row = self.db.execute_one(query, (entity_id,))
        return Plan.from_db(row) if row else None

    def get_by_name(self, name: str) -> Optional[Plan]:
        query = "SELECT * FROM plans WHERE name = ?;"
        row = self.db.execute_one(query, (name.strip(),))
        return Plan.from_db(row) if row else None

    def get_all(self) -> List[Plan]:
        query = "SELECT * FROM plans ORDER BY price ASC;"
        rows = self.db.execute_query(query)
        return [Plan.from_db(row) for row in rows]

    def update(self, entity: Plan) -> bool:
        if entity.id is None:
            return False
        query = """
            UPDATE plans
            SET name = ?, duration_days = ?, price = ?
            WHERE id = ?;
        """
        rows_affected = self.db.execute_non_query(
            query, (entity.name, entity.duration_days, entity.price, entity.id)
        )
        return rows_affected > 0

    def delete(self, entity_id: int) -> bool:
        query = "DELETE FROM plans WHERE id = ?;"
        rows_affected = self.db.execute_non_query(query, (entity_id,))
        return rows_affected > 0
