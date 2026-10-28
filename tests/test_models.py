"""Unit tests for Domain Models and OOP Principles."""
import pytest
from models import BaseEntity, Member, Person, Plan, Subscription


class TestOOPModels:
    """Verifies Classes, Objects, Inheritance, Encapsulation, and Polymorphism."""

    def test_inheritance_hierarchy(self):
        """Tests that Member inherits from Person, and Person inherits from BaseEntity."""
        assert issubclass(Person, BaseEntity)
        assert issubclass(Member, Person)
        assert issubclass(Member, BaseEntity)
        assert issubclass(Plan, BaseEntity)
        assert issubclass(Subscription, BaseEntity)

    def test_person_encapsulation_and_validation(self):
        """Tests encapsulation in Person: validation of name, phone, age."""
        person = Person(full_name="Kareem Tarek", phone="01011223344", age=25, gender="Male")
        assert person.full_name == "Kareem Tarek"
        assert person.phone == "01011223344"
        assert person.age == 25
        assert person.gender == "Male"

        # Test invalid name
        with pytest.raises(ValueError, match="Full name cannot be empty"):
            person.full_name = "   "

        # Test invalid phone
        with pytest.raises(ValueError, match="Phone number cannot be empty"):
            person.phone = ""

        # Test invalid age
        with pytest.raises(ValueError, match="Age must be between 0 and 130"):
            person.age = -5

        with pytest.raises(ValueError, match="Age must be between 0 and 130"):
            person.age = 200

    def test_member_attributes_and_active_status(self):
        """Tests Member subclass behavior, to_dict, and subscription status calculation."""
        # Active member with future date
        active_member = Member(
            full_name="Sara Hassan",
            phone="01199887766",
            plan="Gold",
            expiry="2099-12-31",
        )
        assert active_member.is_active() is True
        assert active_member.plan == "Gold"

        # Expired member
        expired_member = Member(
            full_name="Omar Nader",
            phone="01233445566",
            plan="Basic",
            expiry="2020-01-01",
        )
        assert expired_member.is_active() is False

        # Member with no subscription
        new_member = Member(full_name="Ramy Adel", phone="01511223344")
        assert new_member.is_active() is False
        assert new_member.plan == "-"

    def test_member_serialization_and_deserialization(self):
        """Tests from_db and to_dict polymorphism."""
        raw_db_row = {
            "id": 10,
            "full_name": "Nour Ali",
            "phone": "01055554444",
            "age": 22,
            "gender": "Female",
            "created_at": "2026-01-15 10:30:00",
            "plan": "Premium",
            "expiry": "2026-02-14",
        }

        member = Member.from_db(raw_db_row)
        assert member.id == 10
        assert member.full_name == "Nour Ali"
        assert member.phone == "01055554444"
        assert member.plan == "Premium"
        assert member.expiry == "2026-02-14"

        data_dict = member.to_dict()
        assert data_dict["id"] == 10
        assert data_dict["full_name"] == "Nour Ali"
        assert "is_active" in data_dict

    def test_plan_encapsulation_and_validation(self):
        """Tests Plan model properties and validation."""
        plan = Plan(name="VIP", duration_days=60, price=650.0)
        assert plan.name == "VIP"
        assert plan.duration_days == 60
        assert plan.price == 650.0

        with pytest.raises(ValueError, match="Plan name cannot be empty"):
            plan.name = ""

        with pytest.raises(ValueError, match="Plan duration must be positive"):
            plan.duration_days = 0

        with pytest.raises(ValueError, match="Plan price cannot be negative"):
            plan.price = -10.0

    def test_subscription_creation(self):
        """Tests Subscription instantiation and serialization."""
        sub = Subscription(
            member_id=1,
            plan_id=2,
            start_date="2026-01-01",
            end_date="2026-01-31",
            payment_status="Paid",
            price_paid=350.0,
        )
        assert sub.member_id == 1
        assert sub.plan_id == 2
        assert sub.price_paid == 350.0
        data = sub.to_dict()
        assert data["payment_status"] == "Paid"
