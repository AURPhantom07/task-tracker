"""Save and load TaskList to/from JSON with robust error handling."""
import json
import logging
from pathlib import Path
from typing import Any
from datetime import date

from .models import TaskList
from .exceptions import StorageError, ValidationError

logger = logging.getLogger(__name__)

# Custom JSON encoder for date objects
class DateEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

def save_tasks(task_list: TaskList, path: str) -> None:
    """Write the task list to a JSON file."""
    try:
        data = task_list.to_dict_list()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, cls=DateEncoder)
        logger.info(f"Saved {len(task_list)} tasks to {path}")
    except (OSError, TypeError) as e:
        raise StorageError(f"Failed to save tasks: {e}") from e

def load_tasks(path: str) -> TaskList:
    """Load a TaskList from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise StorageError("Invalid JSON: expected an array of tasks")
        task_list = TaskList.from_dict_list(data)
        logger.info(f"Loaded {len(task_list)} tasks from {path}")
        return task_list
    except FileNotFoundError:
        # If file doesn't exist, return empty list (not an error)
        logger.warning(f"File {path} not found; starting with empty task list.")
        return TaskList()
    except json.JSONDecodeError as e:
        raise StorageError(f"Invalid JSON in {path}: {e}") from e
    except ValidationError as e:
        raise StorageError(f"Task data validation failed: {e}") from e
    except OSError as e:
        raise StorageError(f"Failed to read {path}: {e}") from e