"""Task registry — a simplified task management system.

This module is fully functional. Your job is to add type hints to every
function/method signature (parameters and return types). The docstrings
describe the expected types.
"""


class Task:
    """Represents a single task.

    Attributes:
        task_id: A unique string identifier.
        title: Human-readable task title.
        assignee: Username of the person assigned, or None if unassigned.
        priority: Integer priority (1=highest, 5=lowest).
        tags: List of string tags.
        completed: Whether the task is done.
    """

    def __init__(self, task_id, title, assignee=None, priority=3, tags=None):
        self.task_id = task_id
        self.title = title
        self.assignee = assignee
        self.priority = priority
        self.tags = tags if tags is not None else []
        self.completed = False

    def complete(self):
        """Mark the task as completed. Returns None."""
        self.completed = True

    def add_tag(self, tag):
        """Add a string tag to this task. Returns None."""
        if tag not in self.tags:
            self.tags.append(tag)


class TaskRegistry:
    """A registry that manages Task objects."""

    def __init__(self):
        self._tasks = {}  # maps task_id (str) -> Task

    def register(self, task):
        """Add a Task to the registry. Returns None.

        Raises ValueError if a task with the same ID already exists.
        """
        if task.task_id in self._tasks:
            raise ValueError(f"Task {task.task_id} already registered")
        self._tasks[task.task_id] = task

    def get(self, task_id):
        """Return the Task with the given ID, or None if not found."""
        return self._tasks.get(task_id)

    def find_by_assignee(self, assignee):
        """Return a list of Tasks assigned to the given username."""
        return [t for t in self._tasks.values() if t.assignee == assignee]

    def find_by_tag(self, tag):
        """Return a list of Tasks that have the given tag."""
        return [t for t in self._tasks.values() if tag in t.tags]

    def find_by_priority(self, max_priority):
        """Return a list of Tasks with priority <= max_priority (lower number = higher priority)."""
        return [t for t in self._tasks.values() if t.priority <= max_priority]

    def pending_count(self):
        """Return the number of tasks that are not yet completed."""
        return sum(1 for t in self._tasks.values() if not t.completed)

    def reassign(self, task_id, new_assignee):
        """Reassign a task to a new user (string username).

        Returns True if the task was found and reassigned, False otherwise.
        """
        task = self.get(task_id)
        if task is None:
            return False
        task.assignee = new_assignee
        return True

    def summary(self):
        """Return a dict mapping assignee names (strings) to their count of
        pending tasks (int).

        Unassigned tasks (assignee is None) are grouped under the key
        'unassigned'.
        """
        result = {}
        for task in self._tasks.values():
            if task.completed:
                continue
            key = task.assignee if task.assignee is not None else "unassigned"
            result[key] = result.get(key, 0) + 1
        return result
