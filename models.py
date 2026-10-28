"""Domain Models for GymFlow-v2.
Demonstrates the Four Core OOP Principles:
1. Abstraction: BaseEntity abstract base class defining required contract.
2. Inheritance: BaseEntity -> Person -> Member.
3. Encapsulation: Private/protected attributes with property getters/setters and validation.
4. Polymorphism: Overridden methods (to_dict, from_db, str representations).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Optional


class BaseEntity(ABC):
    """Abstract Base Class for all domain entities.
    Demonstrates OOP Principle: Abstraction.
    """

    def __init__(self, id: Optional[int] = None, created_at: Optional[str] = None):
        self._id = id
        self._created_at = created_at

    @property
    def id(self) -> Optional[int]:
        """Encapsulated getter for entity ID."""
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        """Encapsulated setter for entity ID."""
        if value is not None and value <= 0:
            raise ValueError("Entity ID must be a positive integer.")
        self._id = value

    @property
    def created_at(self) -> Optional[str]:
        return self._created_at

    @created_at.setter
    def created_at(self, value: Optional[str]):
        self._created_at = value

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Abstract method to serialize entity to dictionary."""
        pass

    @classmethod
    @abstractmethod
    def from_db(cls, row: Dict[str, Any]) -> "BaseEntity":
        """Abstract factory method to instantiate entity from database row."""
        pass


class Person(BaseEntity):
    """Represents a human individual in the system.
    Demonstrates OOP Principle: Inheritance (inherits from BaseEntity)
    and Encapsulation (protected fields with validation).
    """

    def __init__(
        self,
        full_name: str = "",
        phone: str = "",
        age: int = 0,
        gender: str = "Unknown",
        id: Optional[int] = None,
        created_at: Optional[str] = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self._full_name = full_name.strip()
        self._phone = phone.strip()
        self._age = age
        self._gender = gender.strip() if gender else "Unknown"

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Full name cannot be empty.")
        self._full_name = value.strip()

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Phone number cannot be empty.")
        self._phone = cleaned

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        if value < 0 or value > 130:
            raise ValueError("Age must be between 0 and 130.")
        self._age = value

    @property
    def gender(self) -> str:
        return self._gender

    @gender.setter
    def gender(self, value: str):
        self._gender = value.strip() if value else "Unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "phone": self.phone,
            "age": self.age,
            "gender": self.gender,
            "created_at": self.created_at,
        }

    @classmethod
    def from_db(cls, row: Dict[str, Any]) -> "Person":
        return cls(
            id=row.get("id"),
            full_name=row.get("full_name", ""),
            phone=row.get("phone", ""),
            age=int(row.get("age") or 0),
            gender=row.get("gender", "Unknown"),
            created_at=str(row.get("created_at")) if row.get("created_at") else None,
        )


class Member(Person):
    """Represents a gym member.
    Demonstrates OOP Principle: Inheritance (inherits from Person and BaseEntity).
    Encapsulates subscription display attributes and active status checks.
    """

    def __init__(
        self,
        full_name: str = "",
        phone: str = "",
        age: int = 0,
        gender: str = "Unknown",
        plan: str = "-",
        expiry: str = "-",
        id: Optional[int] = None,
        created_at: Optional[str] = None,
    ):
        super().__init__(
            full_name=full_name,
            phone=phone,
            age=age,
            gender=gender,
            id=id,
            created_at=created_at,
        )
        self.plan = plan if plan else "-"
        self.expiry = str(expiry) if expiry else "-"

    def is_active(self) -> bool:
        """Determines whether the member's subscription is currently active."""
        if not self.expiry or self.expiry == "-":
            return False
        try:
            exp_date = datetime.strptime(self.expiry, "%Y-%m-%d").date()
            return exp_date >= date.today()
        except (ValueError, TypeError):
            return False

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "plan": self.plan,
            "expiry": self.expiry,
            "is_active": self.is_active(),
        })
        return base

    @classmethod
    def from_db(cls, row: Dict[str, Any]) -> "Member":
        return cls(
            id=row.get("id"),
            full_name=row.get("full_name", ""),
            phone=row.get("phone", ""),
            age=int(row.get("age") or 0),
            gender=row.get("gender", "Unknown"),
            created_at=str(row.get("created_at")) if row.get("created_at") else None,
            plan=str(row.get("plan")) if row.get("plan") is not None else "-",
            expiry=str(row.get("expiry")) if row.get("expiry") is not None else "-",
        )

    def __repr__(self) -> str:
        return f"<Member id={self.id} name='{self.full_name}' phone='{self.phone}' plan='{self.plan}'>"


class Plan(BaseEntity):
    """Represents a Gym Membership Plan entity."""

    def __init__(
        self,
        name: str = "",
        duration_days: int = 30,
        price: float = 0.0,
        id: Optional[int] = None,
        created_at: Optional[str] = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self._name = name.strip()
        self._duration_days = duration_days
        self._price = float(price)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Plan name cannot be empty.")
        self._name = value.strip()

    @property
    def duration_days(self) -> int:
        return self._duration_days

    @duration_days.setter
    def duration_days(self, value: int):
        if value <= 0:
            raise ValueError("Plan duration must be positive.")
        self._duration_days = value

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Plan price cannot be negative.")
        self._price = float(value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "duration_days": self.duration_days,
            "price": self.price,
            "created_at": self.created_at,
        }

    @classmethod
    def from_db(cls, row: Dict[str, Any]) -> "Plan":
        return cls(
            id=row.get("id"),
            name=row.get("name", ""),
            duration_days=int(row.get("duration_days") or 30),
            price=float(row.get("price") or 0.0),
            created_at=str(row.get("created_at")) if row.get("created_at") else None,
        )


class Subscription(BaseEntity):
    """Represents a gym membership subscription."""

    def __init__(
        self,
        member_id: int,
        plan_id: int,
        start_date: str,
        end_date: str,
        payment_status: str = "Paid",
        price_paid: float = 0.0,
        id: Optional[int] = None,
        created_at: Optional[str] = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self.member_id = member_id
        self.plan_id = plan_id
        self.start_date = start_date
        self.end_date = end_date
        self.payment_status = payment_status
        self.price_paid = float(price_paid)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "member_id": self.member_id,
            "plan_id": self.plan_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "payment_status": self.payment_status,
            "price_paid": self.price_paid,
            "created_at": self.created_at,
        }

    @classmethod
    def from_db(cls, row: Dict[str, Any]) -> "Subscription":
        return cls(
            id=row.get("id"),
            member_id=int(row.get("member_id")),
            plan_id=int(row.get("plan_id")),
            start_date=str(row.get("start_date")),
            end_date=str(row.get("end_date")),
            payment_status=str(row.get("payment_status", "Paid")),
            price_paid=float(row.get("price_paid") or 0.0),
            created_at=str(row.get("created_at")) if row.get("created_at") else None,
        )