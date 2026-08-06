from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Member:
    id: Optional[int] = None
    full_name: str = ""
    phone: str = ""
    age: int = 0
    gender: str = ""
    created_at: Optional[str] = None

    # Display information
    plan: str = "-"
    expiry: str = "-"

    @classmethod
    def from_db(cls, row):
        return cls(
            id=row["id"],
            full_name=row["full_name"],
            phone=row["phone"],
            age=row["age"] if "age" in row.keys() else 0,
            gender=row["gender"] if "gender" in row.keys() else "",
            created_at=row["created_at"] if "created_at" in row.keys() else None,
            plan=row["plan"] if "plan" in row.keys() else "-",
            expiry=row["expiry"] if "expiry" in row.keys() else "-"
        )