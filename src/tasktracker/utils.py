"""Recursive utility functions for task trees."""
from typing import List, Optional
from .models import Task

def count_all_tasks(task: Task) -> int:
    """Recursively count tasks including subtasks."""
    total = 1  # count the task itself
    for st in task.subtasks:
        total += count_all_tasks(st)
    return total

def find_task_by_title(tasks: List[Task], title: str) -> Optional[Task]:
    """Recursively search for a task by title (case‑sensitive)."""
    for task in tasks:
        if task.title == title:
            return task
        # Recurse into subtasks
        found = find_task_by_title(task.subtasks, title)
        if found:
            return found
    return None

def render_tree(task: Task, indent: int = 0) -> str:
    """Recursively render a task and its subtasks as a tree string."""
    lines = []
    lines.append("  " * indent + f"• {task.title} (priority {task.priority})")
    for st in task.subtasks:
        lines.append(render_tree(st, indent + 1))
    return "\n".join(lines)

def render_task_list(tasks: List[Task]) -> str:
    """Render a flat list of tasks (for CLI output)."""
    if not tasks:
        return "No tasks."
    lines = []
    for i, t in enumerate(tasks, 1):
        status = "✓" if t.done else "✗"
        lines.append(f"{i:3}. {status} {t.title} | priority {t.priority} | due {t.due}")
    return "\n".join(lines)