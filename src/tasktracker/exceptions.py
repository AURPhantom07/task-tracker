"""Custom exceptions for the task tracker."""

class TaskTrackerError(Exception):
    """Base exception for all task tracker errors."""
    pass

class ValidationError(TaskTrackerError):
    """Raised when input validation fails."""
    pass

class TaskNotFoundError(TaskTrackerError):
    """Raised when a task cannot be found."""
    pass

class StorageError(TaskTrackerError):
    """Raised when file I/O or JSON operations fail."""
    pass