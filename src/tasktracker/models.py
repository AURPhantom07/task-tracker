"""Task, RecurringTask, and TaskList classes."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Iterator
import logging

from .exceptions import ValidationError

logger = logging.getLogger(__name__)

# ---------- Validation helpers ----------
def validate_priority(priority: int) -> None:
    if not 1 <= priority <= 5:
        raise ValidationError("Priority must be between 1 and 5")

def validate_due_date(due: date) -> None:
    if due < date.today():
        raise ValidationError("Due date cannot be in the past")

# ---------- Task (dataclass) ----------
@dataclass
class Task:
    title: str
    priority: int
    due: date
    done: bool = False
    subtasks: List['Task'] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate priority and due date after initialization."""
        validate_priority(self.priority)
        validate_due_date(self.due)
        for st in self.subtasks:
            if not isinstance(st, Task):
                raise ValidationError("Subtask must be a Task instance")

    # --- @property for overdue (this fulfills the requirement) ---
    @property
    def overdue(self) -> bool:
        return not self.done and self.due < date.today()

    # --- Dunder methods (at least 5) ---
    def __repr__(self) -> str:
        return (f"Task(title={self.title!r}, priority={self.priority}, "
                f"due={self.due.isoformat()}, done={self.done})")

    def __str__(self) -> str:
        status = "✓" if self.done else "✗"
        return f"[{status}] {self.title} (priority {self.priority}, due {self.due})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return (self.title == other.title and
                self.priority == other.priority and
                self.due == other.due and
                self.done == other.done)

    def __lt__(self, other: Task) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.due < other.due

    def __hash__(self) -> int:
        return hash((self.title, self.priority, self.due))

    # --- Alternate constructor from dict ---
    @classmethod
    def from_dict(cls, data: dict) -> Task:
        subtasks_data = data.pop("subtasks", [])
        due = date.fromisoformat(data["due"])
        task = cls(title=data["title"], priority=data["priority"],
                   due=due, done=data.get("done", False))
        for st_data in subtasks_data:
            task.subtasks.append(cls.from_dict(st_data))
        return task

    # --- to_dict for serialization ---
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "priority": self.priority,
            "due": self.due.isoformat(),
            "done": self.done,
            "subtasks": [st.to_dict() for st in self.subtasks],
        }


# ---------- RecurringTask (inherits from Task) ----------
@dataclass
class RecurringTask(Task):
    interval_days: int = 7

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.interval_days <= 0:
            raise ValidationError("Interval must be positive")

    def next_occurrence(self) -> date:
        if not self.done:
            return self.due
        next_due = self.due
        while next_due <= date.today():
            next_due += timedelta(days=self.interval_days)
        return next_due

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["interval_days"] = self.interval_days
        base["_class"] = "RecurringTask"
        return base

    @classmethod
    def from_dict(cls, data: dict) -> RecurringTask:
        subtasks_data = data.pop("subtasks", [])
        due = date.fromisoformat(data["due"])
        task = cls(title=data["title"], priority=data["priority"],
                   due=due, done=data.get("done", False),
                   interval_days=data.get("interval_days", 7))
        for st_data in subtasks_data:
            task.subtasks.append(Task.from_dict(st_data))
        return task


# ---------- TaskList (container) ----------
class TaskList:
    def __init__(self, tasks: Optional[List[Task]] = None) -> None:
        self._tasks: List[Task] = tasks or []

    def add(self, task: Task) -> None:
        self._tasks.append(task)
        self._tasks.sort()

    def pending(self) -> List[Task]:
        return [t for t in self._tasks if not t.done]

    def all_tasks(self) -> List[Task]:
        return self._tasks

    def find_by_title(self, title: str) -> Optional[Task]:
        from .utils import find_task_by_title
        return find_task_by_title(self._tasks, title)

    def __len__(self) -> int:
        return len(self._tasks)

    def __iter__(self) -> Iterator[Task]:
        return iter(self._tasks)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Task):
            return False
        return any(t == item for t in self._tasks)

    def __repr__(self) -> str:
        return f"TaskList({len(self)} tasks)"

    @classmethod
    def from_dict_list(cls, data: List[dict]) -> TaskList:
        tasks = []
        for item in data:
            if item.get("_class") == "RecurringTask":
                tasks.append(RecurringTask.from_dict(item))
            else:
                tasks.append(Task.from_dict(item))
        return cls(tasks)

    def to_dict_list(self) -> List[dict]:
        return [t.to_dict() for t in self._tasks]

    def save(self, path: str) -> None:
        from .storage import save_tasks
        save_tasks(self, path)

    @classmethod
    def load(cls, path: str) -> TaskList:
        from .storage import load_tasks
        return load_tasks(path)