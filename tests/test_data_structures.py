"""Unit tests for Custom Data Structures: Dictionary Index, LIFO Stack, and FIFO Queue."""
import pytest
from core.data_structures import ActivityLog, ActivityQueue, MemberLookupIndex, UndoAction, UndoStack
from models import Member


class TestDataStructures:

    # =========================================================================
    # 1. Dictionary: MemberLookupIndex
    # =========================================================================

    def test_member_lookup_index_operations(self):
        """Tests O(1) Dictionary lookups by ID and phone, update, and removal."""
        index = MemberLookupIndex()
        assert len(index) == 0

        m1 = Member(id=1, full_name="Ali Mostafa", phone="01011112222", plan="Gold")
        m2 = Member(id=2, full_name="Hany Adel", phone="01233334444", plan="Basic")

        # Put items
        index.put(m1)
        index.put(m2)
        assert len(index) == 2

        # Fast O(1) lookups
        assert index.get_by_id(1) is m1
        assert index.get_by_id(2) is m2
        assert index.get_by_id(999) is None

        assert index.get_by_phone("01011112222") is m1
        assert index.get_by_phone("01233334444") is m2
        assert index.get_by_phone("00000000000") is None

        # Removal
        removed = index.remove(1)
        assert removed is m1
        assert index.get_by_id(1) is None
        assert index.get_by_phone("01011112222") is None
        assert len(index) == 1

        # Rebuild bulk
        m3 = Member(id=3, full_name="Tarek Ziad", phone="01555556666")
        index.rebuild([m1, m2, m3])
        assert len(index) == 3
        assert len(index.all()) == 3

    # =========================================================================
    # 2. Stack: UndoStack (LIFO)
    # =========================================================================

    def test_undo_stack_lifo_order(self):
        """Tests that UndoStack exhibits exact Last-In, First-Out (LIFO) behavior."""
        stack = UndoStack(max_capacity=10)
        assert stack.is_empty() is True
        assert stack.size() == 0

        executed_actions = []

        action1 = UndoAction(description="Action 1", undo_callable=lambda: executed_actions.append(1))
        action2 = UndoAction(description="Action 2", undo_callable=lambda: executed_actions.append(2))
        action3 = UndoAction(description="Action 3", undo_callable=lambda: executed_actions.append(3))

        stack.push(action1)
        stack.push(action2)
        stack.push(action3)

        assert stack.size() == 3
        assert stack.peek() is action3

        # Pop should yield in reverse order: 3, 2, 1
        popped = stack.pop()
        assert popped is action3
        popped.undo_callable()

        popped = stack.pop()
        assert popped is action2
        popped.undo_callable()

        popped = stack.pop()
        assert popped is action1
        popped.undo_callable()

        assert stack.is_empty() is True
        assert executed_actions == [3, 2, 1]

    def test_undo_stack_capacity_eviction(self):
        """Tests that UndoStack respects maximum capacity and evicts oldest."""
        stack = UndoStack(max_capacity=3)
        for i in range(5):
            stack.push(UndoAction(description=f"Action {i}", undo_callable=lambda: None))

        assert stack.size() == 3
        # Oldest (0 and 1) evicted, remaining: 2, 3, 4
        assert stack.pop().description == "Action 4"
        assert stack.pop().description == "Action 3"
        assert stack.pop().description == "Action 2"
        assert stack.pop() is None

    # =========================================================================
    # 3. Queue: ActivityQueue (FIFO)
    # =========================================================================

    def test_activity_queue_fifo_order(self):
        """Tests that ActivityQueue exhibits First-In, First-Out (FIFO) behavior."""
        queue = ActivityQueue()
        assert queue.is_empty() is True

        log1 = ActivityLog(action_type="CREATE", entity_name="Member", entity_id=1, description="Added Ali")
        log2 = ActivityLog(action_type="RENEW", entity_name="Subscription", entity_id=1, description="Renewed Gold")
        log3 = ActivityLog(action_type="DELETE", entity_name="Member", entity_id=2, description="Deleted Hany")

        queue.enqueue(log1)
        queue.enqueue(log2)
        queue.enqueue(log3)

        assert queue.size() == 3
        assert queue.peek() is log1

        # Dequeue in FIFO order: 1, then 2, then 3
        assert queue.dequeue() is log1
        assert queue.dequeue() is log2
        assert queue.dequeue() is log3
        assert queue.dequeue() is None
        assert queue.is_empty() is True

    def test_activity_queue_drain(self):
        """Tests batch drain operation of ActivityQueue."""
        queue = ActivityQueue()
        queue.enqueue(ActivityLog(action_type="TEST", entity_name="E", entity_id=1, description="D1"))
        queue.enqueue(ActivityLog(action_type="TEST", entity_name="E", entity_id=2, description="D2"))

        drained = queue.drain()
        assert len(drained) == 2
        assert queue.is_empty() is True
