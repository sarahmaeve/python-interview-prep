# Solution 14 --- Adding Type Hints to `task_registry.py`

## Complete Type Annotations

```python
from __future__ import annotations


class Task:
    def __init__(
        self,
        task_id: str,
        title: str,
        assignee: str | None = None,
        priority: int = 3,
        tags: list[str] | None = None,
    ) -> None:
        self.task_id = task_id
        self.title = title
        self.assignee = assignee
        self.priority = priority
        self.tags = tags if tags is not None else []
        self.completed = False

    def complete(self) -> None:
        self.completed = True

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)


class TaskRegistry:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def register(self, task: Task) -> None:
        if task.task_id in self._tasks:
            raise ValueError(f"Task {task.task_id} already registered")
        self._tasks[task.task_id] = task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def find_by_assignee(self, assignee: str) -> list[Task]:
        return [t for t in self._tasks.values() if t.assignee == assignee]

    def find_by_tag(self, tag: str) -> list[Task]:
        return [t for t in self._tasks.values() if tag in t.tags]

    def find_by_priority(self, max_priority: int) -> list[Task]:
        return [t for t in self._tasks.values() if t.priority <= max_priority]

    def pending_count(self) -> int:
        return sum(1 for t in self._tasks.values() if not t.completed)

    def reassign(self, task_id: str, new_assignee: str) -> bool:
        task = self.get(task_id)
        if task is None:
            return False
        task.assignee = new_assignee
        return True

    def summary(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for task in self._tasks.values():
            if task.completed:
                continue
            key = task.assignee if task.assignee is not None else "unassigned"
            result[key] = result.get(key, 0) + 1
        return result
```

---

## Key Decisions

| Type choice | Reasoning |
|---|---|
| `assignee: str \| None` | The parameter defaults to `None` (unassigned). `Optional[str]` / `str \| None` tells mypy that code must handle the `None` case before calling string methods. |
| `tags: list[str] \| None` | The default is `None` (not `[]`) to avoid the mutable default argument pitfall. The hint must reflect that callers may pass `None`. |
| `-> list[Task]` not `-> list` | A bare `list` provides no information about element types. `list[Task]` lets mypy verify that callers treat elements as `Task` objects. |
| `-> None` on mutating methods | Explicit `-> None` documents that the method operates via side effects. Without it, mypy treats the return type as `Any`, weakening checks. |
| `-> Task \| None` on `get()` | The method may return `None` for missing IDs. This forces callers to narrow the type (e.g. `if task is not None:`) before using the result. |
| `dict[str, int]` on `summary()` | A bare `dict` hides what keys and values look like. The parameterized type catches mistakes like returning `{name: [list_of_tasks]}`. |

---

## Common Mistakes

1. **Forgetting `Optional` for nullable parameters.** Writing `assignee: str = None` without the `Optional`/`| None` wrapper causes mypy to flag the default as incompatible.

2. **Using bare `list` or `dict`.** These are equivalent to `list[Any]` / `dict[Any, Any]` and defeat the purpose of type checking.

3. **Omitting return types.** Without `-> None`, mypy infers `-> None` only sometimes. Explicit annotations prevent accidental `Any` return types.

4. **Mutable default in the signature.** `tags: list[str] = []` is a classic Python bug. The correct pattern is `tags: list[str] | None = None` with a runtime guard.

5. **Annotating `self`.** You should *not* annotate `self` -- mypy infers it automatically.

---

## Bonus: What mypy Catches Now

```python
# 1. Passing wrong type to register
registry.register("not a Task")  # error: Argument 1 has incompatible type "str"; expected "Task"

# 2. Using get() result without None check
task = registry.get("T-1")
print(task.title)  # error: "Task | None" has no attribute "title"

# 3. Assigning wrong type to priority
Task("T-1", "Do stuff", priority="high")  # error: Argument "priority" has incompatible type "str"; expected "int"

# 4. Treating summary values as strings
for name, count in registry.summary().items():
    print(name + ": " + count)  # error: Unsupported operand types for + ("str" and "int")
```

Each of these would silently pass at import time without annotations but crash at
runtime. With type hints, mypy catches them before the code ever runs.
