"""Base Repository Interface demonstrating Abstraction and the Repository Pattern."""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract generic repository defining standard CRUD contract.
    Demonstrates OOP Principle: Abstraction and the GoF Repository Pattern.
    """

    @abstractmethod
    def add(self, entity: T) -> int:
        """Persists a new entity and returns its generated identifier."""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Retrieves a single entity by its primary key ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieves all entities of this type."""
        pass

    @abstractmethod
    def update(self, entity: T) -> bool:
        """Updates an existing entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Deletes an entity by ID."""
        pass
