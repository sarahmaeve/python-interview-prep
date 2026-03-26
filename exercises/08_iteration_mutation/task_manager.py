from datetime import datetime


class TaskManager:
    """Manages a list of task dictionaries."""

    def __init__(self):
        self.tasks = []

    def add_task(self, task_id, title, assignee, due_date, status="pending"):
        """Add a task dictionary to the task list."""
        self.tasks.append({
            "task_id": task_id,
            "title": title,
            "assignee": assignee,
            "due_date": due_date,
            "status": status,
        })

    def complete_task(self, task_id):
        """Mark a task as completed by its task_id."""
        for task in self.tasks:
            if task["task_id"] == task_id:
                task["status"] = "completed"
                return
        raise ValueError(f"Task {task_id} not found")

    def remove_completed(self):
        """Remove all completed tasks from the list."""
        for task in self.tasks:
            if task["status"] == "completed":
                self.tasks.remove(task)

    def get_overdue(self, today):
        """Return a list of tasks whose due_date is before *today*.

        Dates are strings in ``MM/DD/YYYY`` format.
        """
        overdue = []
        for task in self.tasks:
            if task["due_date"] < today:
                overdue.append(task)
        return overdue

    def bulk_reassign(self, from_user, to_user):
        """Reassign every task owned by *from_user* to *to_user*.

        Returns the number of tasks reassigned.
        """
        matching = (t for t in self.tasks if t["assignee"] == from_user)

        count = sum(1 for _ in matching)

        for task in matching:
            task["assignee"] = to_user

        return count
