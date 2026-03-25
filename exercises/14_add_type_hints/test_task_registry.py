"""Tests for task_registry.py — both behaviour and type annotations."""

import sys
import types
import typing
import unittest

from task_registry import Task, TaskRegistry


# ---------------------------------------------------------------------------
# Helpers for annotation comparison
# ---------------------------------------------------------------------------

def _is_optional_of(hint, inner_type):
    """Return True if *hint* is Optional[inner_type] (i.e. Union[inner_type, None]).

    Handles both ``Optional[X]`` and ``X | None`` (Python 3.10+).
    """
    origin = typing.get_origin(hint)

    # typing.Optional[X] -> typing.Union[X, None]
    if origin is typing.Union:
        args = typing.get_args(hint)
        return set(args) == {inner_type, type(None)}

    # Python 3.10+ union syntax:  X | None  -> types.UnionType
    if sys.version_info >= (3, 10):
        if isinstance(hint, types.UnionType):
            args = typing.get_args(hint)
            return set(args) == {inner_type, type(None)}

    return False


def _is_list_of(hint, item_type):
    """Return True if *hint* is list[item_type]."""
    return typing.get_origin(hint) is list and typing.get_args(hint) == (item_type,)


def _is_dict_of(hint, key_type, val_type):
    """Return True if *hint* is dict[key_type, val_type]."""
    return typing.get_origin(hint) is dict and typing.get_args(hint) == (key_type, val_type)


# ===========================================================================
# Category 1 — Behavioural tests (the code works correctly)
# ===========================================================================

class TestTaskBehaviour(unittest.TestCase):
    """Verify that the task registry code is functionally correct."""

    def setUp(self):
        self.registry = TaskRegistry()
        self.t1 = Task("T-1", "Write docs", assignee="alice", priority=2, tags=["docs"])
        self.t2 = Task("T-2", "Fix login bug", assignee="bob", priority=1, tags=["bug", "urgent"])
        self.t3 = Task("T-3", "Add feature", assignee="alice", priority=3, tags=["feature"])
        self.t4 = Task("T-4", "Triage issues", priority=4)
        for t in (self.t1, self.t2, self.t3, self.t4):
            self.registry.register(t)

    def test_register_and_get(self):
        """Registering a task and retrieving it by ID returns the same object."""
        self.assertIs(self.registry.get("T-1"), self.t1)

    def test_get_missing_returns_none(self):
        """Getting a non-existent task ID returns None."""
        self.assertIsNone(self.registry.get("NOPE"))

    def test_find_by_assignee(self):
        """find_by_assignee returns only tasks belonging to that user."""
        result = self.registry.find_by_assignee("alice")
        self.assertEqual(sorted(t.task_id for t in result), ["T-1", "T-3"])

    def test_pending_count_reflects_completion(self):
        """pending_count decreases as tasks are completed."""
        self.assertEqual(self.registry.pending_count(), 4)
        self.t1.complete()
        self.t2.complete()
        self.assertEqual(self.registry.pending_count(), 2)

    def test_reassign_existing_task(self):
        """reassign returns True and updates the assignee for a known task."""
        self.assertTrue(self.registry.reassign("T-4", "carol"))
        self.assertEqual(self.t4.assignee, "carol")

    def test_reassign_missing_task(self):
        """reassign returns False for an unknown task ID."""
        self.assertFalse(self.registry.reassign("NOPE", "carol"))

    def test_summary_groups_correctly(self):
        """summary groups pending tasks by assignee; None becomes 'unassigned'."""
        self.t2.complete()
        expected = {"alice": 2, "unassigned": 1}
        self.assertEqual(self.registry.summary(), expected)


# ===========================================================================
# Category 2 — Type-annotation tests
# ===========================================================================

class TestTypeAnnotations(unittest.TestCase):
    """Verify that proper type hints have been added to all signatures."""

    # -- Task class ----------------------------------------------------------

    def test_task_init_annotations(self):
        """Task.__init__ should annotate all parameters with correct types."""
        hints = typing.get_type_hints(Task.__init__)

        self.assertIn("task_id", hints, "Task.__init__ is missing annotation for 'task_id'")
        self.assertEqual(hints["task_id"], str,
                         "Task.__init__ task_id should be str")

        self.assertIn("title", hints, "Task.__init__ is missing annotation for 'title'")
        self.assertEqual(hints["title"], str,
                         "Task.__init__ title should be str")

        self.assertIn("assignee", hints, "Task.__init__ is missing annotation for 'assignee'")
        self.assertTrue(
            _is_optional_of(hints["assignee"], str),
            "Task.__init__ assignee should be Optional[str] (or str | None)",
        )

        self.assertIn("priority", hints, "Task.__init__ is missing annotation for 'priority'")
        self.assertEqual(hints["priority"], int,
                         "Task.__init__ priority should be int")

        self.assertIn("tags", hints, "Task.__init__ is missing annotation for 'tags'")
        self.assertTrue(
            _is_optional_of(hints["tags"], list[str]),
            "Task.__init__ tags should be Optional[list[str]] (or list[str] | None)",
        )

    def test_task_complete_return(self):
        """Task.complete should have a return type annotation of None."""
        hints = typing.get_type_hints(Task.complete)
        self.assertIn("return", hints, "Task.complete is missing a return type annotation")
        self.assertIs(hints["return"], type(None),
                      "Task.complete should return None")

    def test_task_add_tag_annotations(self):
        """Task.add_tag should annotate tag: str and return None."""
        hints = typing.get_type_hints(Task.add_tag)

        self.assertIn("tag", hints, "Task.add_tag is missing annotation for 'tag'")
        self.assertEqual(hints["tag"], str,
                         "Task.add_tag tag should be str")

        self.assertIn("return", hints, "Task.add_tag is missing a return type annotation")
        self.assertIs(hints["return"], type(None),
                      "Task.add_tag should return None")

    # -- TaskRegistry class --------------------------------------------------

    def test_registry_register_annotations(self):
        """TaskRegistry.register should annotate task: Task and return None."""
        hints = typing.get_type_hints(TaskRegistry.register)

        self.assertIn("task", hints, "TaskRegistry.register is missing annotation for 'task'")
        self.assertEqual(hints["task"], Task,
                         "TaskRegistry.register task should be Task")

        self.assertIn("return", hints, "TaskRegistry.register is missing a return type annotation")
        self.assertIs(hints["return"], type(None),
                      "TaskRegistry.register should return None")

    def test_registry_get_annotations(self):
        """TaskRegistry.get should have task_id: str and return Optional[Task]."""
        hints = typing.get_type_hints(TaskRegistry.get)

        self.assertIn("task_id", hints, "TaskRegistry.get is missing annotation for 'task_id'")
        self.assertEqual(hints["task_id"], str,
                         "TaskRegistry.get task_id should be str")

        self.assertIn("return", hints, "TaskRegistry.get is missing a return type annotation")
        self.assertTrue(
            _is_optional_of(hints["return"], Task),
            "TaskRegistry.get should return Optional[Task] (or Task | None)",
        )

    def test_registry_find_by_assignee_annotations(self):
        """TaskRegistry.find_by_assignee should return list[Task]."""
        hints = typing.get_type_hints(TaskRegistry.find_by_assignee)

        self.assertIn("assignee", hints,
                      "TaskRegistry.find_by_assignee is missing annotation for 'assignee'")
        self.assertEqual(hints["assignee"], str,
                         "TaskRegistry.find_by_assignee assignee should be str")

        self.assertIn("return", hints,
                      "TaskRegistry.find_by_assignee is missing a return type annotation")
        self.assertTrue(
            _is_list_of(hints["return"], Task),
            "TaskRegistry.find_by_assignee should return list[Task]",
        )

    def test_registry_find_by_tag_annotations(self):
        """TaskRegistry.find_by_tag should return list[Task]."""
        hints = typing.get_type_hints(TaskRegistry.find_by_tag)

        self.assertIn("tag", hints,
                      "TaskRegistry.find_by_tag is missing annotation for 'tag'")
        self.assertEqual(hints["tag"], str,
                         "TaskRegistry.find_by_tag tag should be str")

        self.assertIn("return", hints,
                      "TaskRegistry.find_by_tag is missing a return type annotation")
        self.assertTrue(
            _is_list_of(hints["return"], Task),
            "TaskRegistry.find_by_tag should return list[Task]",
        )

    def test_registry_reassign_annotations(self):
        """TaskRegistry.reassign should return bool."""
        hints = typing.get_type_hints(TaskRegistry.reassign)

        self.assertIn("task_id", hints,
                      "TaskRegistry.reassign is missing annotation for 'task_id'")
        self.assertEqual(hints["task_id"], str,
                         "TaskRegistry.reassign task_id should be str")

        self.assertIn("new_assignee", hints,
                      "TaskRegistry.reassign is missing annotation for 'new_assignee'")
        self.assertEqual(hints["new_assignee"], str,
                         "TaskRegistry.reassign new_assignee should be str")

        self.assertIn("return", hints,
                      "TaskRegistry.reassign is missing a return type annotation")
        self.assertIs(hints["return"], bool,
                      "TaskRegistry.reassign should return bool")

    def test_registry_summary_annotations(self):
        """TaskRegistry.summary should return dict[str, int]."""
        hints = typing.get_type_hints(TaskRegistry.summary)

        self.assertIn("return", hints,
                      "TaskRegistry.summary is missing a return type annotation")
        self.assertTrue(
            _is_dict_of(hints["return"], str, int),
            "TaskRegistry.summary should return dict[str, int]",
        )

    def test_registry_pending_count_annotations(self):
        """TaskRegistry.pending_count should return int."""
        hints = typing.get_type_hints(TaskRegistry.pending_count)

        self.assertIn("return", hints,
                      "TaskRegistry.pending_count is missing a return type annotation")
        self.assertIs(hints["return"], int,
                      "TaskRegistry.pending_count should return int")

    def test_registry_find_by_priority_annotations(self):
        """TaskRegistry.find_by_priority should have max_priority: int and return list[Task]."""
        hints = typing.get_type_hints(TaskRegistry.find_by_priority)

        self.assertIn("max_priority", hints,
                      "TaskRegistry.find_by_priority is missing annotation for 'max_priority'")
        self.assertEqual(hints["max_priority"], int,
                         "TaskRegistry.find_by_priority max_priority should be int")

        self.assertIn("return", hints,
                      "TaskRegistry.find_by_priority is missing a return type annotation")
        self.assertTrue(
            _is_list_of(hints["return"], Task),
            "TaskRegistry.find_by_priority should return list[Task]",
        )


if __name__ == "__main__":
    unittest.main()
