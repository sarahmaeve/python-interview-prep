import unittest
from task_manager import TaskManager


class TestAddAndComplete(unittest.TestCase):
    def test_add_single_task(self):
        tm = TaskManager()
        tm.add_task("T1", "Write docs", "alice", "06/15/2026")
        self.assertEqual(len(tm.tasks), 1)
        self.assertEqual(tm.tasks[0]["title"], "Write docs")
        self.assertEqual(tm.tasks[0]["status"], "pending")

    def test_complete_task(self):
        tm = TaskManager()
        tm.add_task("T1", "Write docs", "alice", "06/15/2026")
        tm.complete_task("T1")
        self.assertEqual(tm.tasks[0]["status"], "completed")


class TestRemoveCompleted(unittest.TestCase):
    def test_remove_single_completed(self):
        tm = TaskManager()
        tm.add_task("T1", "A", "alice", "06/15/2026", status="completed")
        tm.add_task("T2", "B", "bob", "06/15/2026", status="pending")
        tm.remove_completed()
        self.assertEqual(len(tm.tasks), 1)
        self.assertEqual(tm.tasks[0]["task_id"], "T2")

    def test_remove_consecutive_completed(self):
        """Two completed tasks in a row — the mutation bug skips the second."""
        tm = TaskManager()
        tm.add_task("T1", "A", "alice", "01/01/2026", status="completed")
        tm.add_task("T2", "B", "bob", "01/01/2026", status="completed")
        tm.add_task("T3", "C", "carol", "01/01/2026", status="pending")
        tm.remove_completed()
        self.assertEqual(len(tm.tasks), 1)
        self.assertEqual(tm.tasks[0]["task_id"], "T3")

    def test_remove_all_completed(self):
        tm = TaskManager()
        tm.add_task("T1", "A", "alice", "01/01/2026", status="completed")
        tm.add_task("T2", "B", "bob", "01/01/2026", status="completed")
        tm.remove_completed()
        self.assertEqual(len(tm.tasks), 0)


class TestGetOverdue(unittest.TestCase):
    def test_overdue_basic(self):
        tm = TaskManager()
        tm.add_task("T1", "Old", "alice", "01/15/2025")
        tm.add_task("T2", "Future", "bob", "12/31/2026")
        overdue = tm.get_overdue("03/25/2026")
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0]["task_id"], "T1")

    def test_overdue_lexicographic_trap(self):
        """Lexicographically '12/01/2025' < '02/01/2026' is True, but
        Dec 2025 is NOT after Feb 2026 — it's before. The buggy code
        would wrongly include 02/01/2026 as overdue or miss 12/01/2025."""
        tm = TaskManager()
        # This task is due Dec 1 2025 — clearly overdue on Mar 25 2026
        tm.add_task("T1", "Dec task", "alice", "12/01/2025")
        # This task is due Feb 1 2027 — NOT overdue on Mar 25 2026
        tm.add_task("T2", "Feb task", "bob", "02/01/2027")
        overdue = tm.get_overdue("03/25/2026")
        ids = [t["task_id"] for t in overdue]
        self.assertIn("T1", ids)
        self.assertNotIn("T2", ids)


class TestBulkReassign(unittest.TestCase):
    def test_bulk_reassign_no_match_returns_zero(self):
        tm = TaskManager()
        tm.add_task("T1", "A", "alice", "06/15/2026")
        count = tm.bulk_reassign("nobody", "carol")
        self.assertEqual(count, 0)
        self.assertEqual(tm.tasks[0]["assignee"], "alice")

    def test_bulk_reassign_returns_count(self):
        tm = TaskManager()
        tm.add_task("T1", "A", "alice", "06/15/2026")
        tm.add_task("T2", "B", "alice", "06/15/2026")
        tm.add_task("T3", "C", "bob", "06/15/2026")
        count = tm.bulk_reassign("alice", "carol")
        self.assertEqual(count, 2)

    def test_bulk_reassign_actually_changes_assignee(self):
        """The generator-exhaustion bug means count is correct but no
        tasks are actually reassigned."""
        tm = TaskManager()
        tm.add_task("T1", "A", "alice", "06/15/2026")
        tm.add_task("T2", "B", "alice", "06/15/2026")
        tm.bulk_reassign("alice", "carol")
        for task in tm.tasks:
            if task["task_id"] in ("T1", "T2"):
                self.assertEqual(task["assignee"], "carol")


if __name__ == "__main__":
    unittest.main()
