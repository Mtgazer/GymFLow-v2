"""Data Structures Module for GymFlow-v2.
Implements domain-tailored data structures:
1. Dictionary: MemberLookupIndex for O(1) hash-based lookups by ID and phone.
2. Stack: UndoStack (LIFO) for undoing user operations.
3. Queue: ActivityQueue (FIFO) for sequential processing of audit/activity events.
"""
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from models import Member

T = TypeVar("T")


class MemberLookupIndex:
    """Dictionary-based in-memory index for Member records.
    Provides O(1) amortized lookup by ID and Phone number.
    Reduces redundant database roundtrips during search and validation.
    """

    def __init__(self):
        self._by_id: Dict[int, Member] = {}
        self._by_phone: Dict[str, Member] = {}

    def put(self, member: Member):
        """Inserts or updates a member in the index. Time Complexity: O(1)."""
        if member.id is not None:
            self._by_id[member.id] = member
        if member.phone:
            self._by_phone[member.phone] = member

    def get_by_id(self, member_id: int) -> Optional[Member]:
        """Retrieves a member by ID. Time Complexity: O(1)."""
        return self._by_id.get(member_id)

    def get_by_phone(self, phone: str) -> Optional[Member]:
        """Retrieves a member by phone. Time Complexity: O(1)."""
        return self._by_phone.get(phone.strip())

    def remove(self, member_id: int) -> Optional[Member]:
        """Removes a member from both indexes. Time Complexity: O(1)."""
        member = self._by_id.pop(member_id, None)
        if member and member.phone in self._by_phone:
            self._by_phone.pop(member.phone, None)
        return member

    def rebuild(self, members: List[Member]):
        """Rebuilds the entire index from a list of members. Time Complexity: O(N)."""
        self._by_id.clear()
        self._by_phone.clear()
        for m in members:
            self.put(m)

    def all(self) -> List[Member]:
        """Returns all members currently indexed. Time Complexity: O(N)."""
        return list(self._by_id.values())

    def __len__(self) -> int:
        return len(self._by_id)

    def clear(self):
        self._by_id.clear()
        self._by_phone.clear()


@dataclass
class UndoAction:
    """Encapsulates an undoable operation with human-readable description
    and a callable to execute the undo.
    """
    description: str
    undo_callable: Callable[[], Any]
    timestamp: datetime = datetime.now()


class UndoStack(Generic[T]):
    """Stack data structure implementing LIFO (Last-In, First-Out) semantics
    for undo operations.
    Enforces a maximum capacity to prevent unbounded memory growth.
    """

    def __init__(self, max_capacity: int = 50):
        self._items: List[T] = []
        self._max_capacity = max_capacity

    def push(self, item: T):
        """Pushes an action onto the stack. Time Complexity: O(1)."""
        if len(self._items) >= self._max_capacity:
            self._items.pop(0)  # Evict oldest action
        self._items.append(item)

    def pop(self) -> Optional[T]:
        """Pops and returns the top action. Time Complexity: O(1)."""
        if self.is_empty():
            return None
        return self._items.pop()

    def peek(self) -> Optional[T]:
        """Inspects the top action without removing it. Time Complexity: O(1)."""
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        """Returns True if the stack has no items. Time Complexity: O(1)."""
        return len(self._items) == 0

    def size(self) -> int:
        """Returns current number of items. Time Complexity: O(1)."""
        return len(self._items)

    def clear(self):
        self._items.clear()


@dataclass
class ActivityLog:
    """Represents an audit log entry in the FIFO event queue."""
    action_type: str
    entity_name: str
    entity_id: Optional[int]
    description: str
    timestamp: datetime = datetime.now()


class ActivityQueue:
    """Queue data structure implementing FIFO (First-In, First-Out) semantics
    for tracking system events, audit logs, and notification tasks.
    Utilizes collections.deque for efficient O(1) appends and pops.
    """

    def __init__(self):
        self._queue: deque = deque()

    def enqueue(self, item: ActivityLog):
        """Adds an item to the tail of the queue. Time Complexity: O(1)."""
        self._queue.append(item)

    def dequeue(self) -> Optional[ActivityLog]:
        """Removes and returns an item from the head of the queue. Time Complexity: O(1)."""
        if self.is_empty():
            return None
        return self._queue.popleft()

    def peek(self) -> Optional[ActivityLog]:
        """Inspects the front item without removal. Time Complexity: O(1)."""
        if self.is_empty():
            return None
        return self._queue[0]

    def is_empty(self) -> bool:
        """Returns True if queue contains no items. Time Complexity: O(1)."""
        return len(self._queue) == 0

    def size(self) -> int:
        """Returns the number of elements in the queue. Time Complexity: O(1)."""
        return len(self._queue)

    def drain(self) -> List[ActivityLog]:
        """Empties all elements and returns them in order. Time Complexity: O(N)."""
        items = list(self._queue)
        self._queue.clear()
        return items
