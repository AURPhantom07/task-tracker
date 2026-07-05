# Task Tracker – Capstone Project

A polished CLI application to manage tasks with subtasks, recurring tasks, and JSON persistence.

## Installation

```bash
# Clone or navigate to your project folder
cd tasktracker

# Install in editable mode
pip install -e .
```

## How to use and examples

# Add a new task
```bash
python -m tasktracker.cli add "Finish report" --priority 1 --due 2026-07-15
```

# Add a recurring task
```bash
python -m tasktracker.cli add "Weekly review" --priority 2 --due 2026-07-12 --interval 7
```
# Add a subtask

```bash
python -m tasktracker.cli add "Write introduction" --parent "Finish report" --due 2026-07-10
```

# List pending tasks
```bash
python -m tasktracker.cli list
```

# Show task tree
```bash
python -m tasktracker.cli show "Finish report"
```


# Mark as done
```bash
python -m tasktracker.cli done "Write introduction"
```

# List all tasks (including done)
```bash
python -m tasktracker.cli list --all
```

# Get current weather for a city 
```bash
python -m tasktracker.cli weather "Miami"
```

```mermaid
classDiagram
    Task <|-- RecurringTask : inherits
    TaskList o-- Task : contains
    class Task {
        +str title
        +int priority
        +date due
        +bool done
        +list~Task~ subtasks
        +__repr__()
        +__str__()
        +__eq__()
        +__lt__()
        +__hash__()
        +from_dict(d)$
        +to_dict()
    }
    class RecurringTask {
        +int interval_days
        +next_occurrence()
        +from_dict(d)$
        +to_dict()
    }
    class TaskList {
        -list~Task~ _tasks
        +add(task)
        +pending()
        +all_tasks()
        +from_dict_list(data)$
        +to_dict_list()
        +__len__()
        +__iter__()
        +__contains__()
    }

```