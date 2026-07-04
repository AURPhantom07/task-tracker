# Architecture Decision Log

## ADR-001: Class Hierarchy – Inheritance vs Composition

**Context.** We need to model recurring tasks. RecurringTask is essentially a Task with an extra interval property.

**Decision.** Use inheritance (RecurringTask extends Task) because it’s a clear "is‑a" relationship and allows reuse of all Task fields and methods.

**Alternatives considered.**
1. Composition – wrap a Task inside a RecurringTask. This would require forwarding all methods, which is verbose.
2. Separate unrelated classes – leads to duplicate code.

**Consequences.** + Simple and DRY. – Subclasses inherit all behavior, but we need to override `__post_init__` and serialization. We accept that.
**Governs:** `src/tasktracker/models.py`

## ADR-002: Persistence – JSON vs CSV vs SQLite

**Context.** Tasks have nested subtasks and date fields. The app is single‑user, local.
**Decision.** Use JSON with the `json` module, storing tasks as a list of dicts.
**Alternatives considered.**
1. CSV – flat, cannot represent nested subtasks without ugly encoding.
2. SQLite – powerful but overkill; adds dependency and schema migration complexity.
**Consequences.** + Human‑readable, zero dependencies, easy to debug. – Whole file rewritten on each save, no concurrency safety (acceptable for single user).
**Governs:** `src/tasktracker/storage.py`

## ADR-003: Recursion – Used for Subtask Traversal

**Context.** Tasks can have subtasks of arbitrary depth. We need to find tasks, count them, and display trees.
**Decision.** Implement recursive functions (find_task_by_title, count_all_tasks, render_tree) because the tree structure is naturally recursive.
**Alternatives considered.**
1. Iterative stack – also possible but less elegant.
2. Store parent pointers – would complicate serialization.
**Consequences.** + Simple, matches the data structure. – Recursion depth limited by Python (but task depth is small in practice).
**Governs:** `src/tasktracker/utils.py`

## ADR-004: Dunder Methods – Which and Why

**Context.** We need to provide natural Python operations and pretty‑printing.
**Decision.** Implement `__repr__`, `__str__`, `__eq__`, `__lt__`, `__hash__` for Task; and `__len__`, `__iter__`, `__contains__` for TaskList.
**Alternatives considered.** We could implement only `__repr__` and `__str__`, but the assignment requires ≥5. Adding `__lt__` enables sorting; `__hash__` allows tasks in sets (though not used, we include it).
**Consequences.** + Better debugging, sorting, and container behavior. – Slight overhead, but negligible.
**Governs:** `src/tasktracker/models.py`

## ADR-005: CLI Library – argparse vs click vs typer

**Context.** The app must be invokable from the terminal with subcommands and flags.
**Decision.** Use `argparse` (standard library) because the assignment specifically mentions it, and it avoids external dependencies.
**Alternatives considered.**
1. Click – more expressive but requires third‑party.
2. Typer – modern but also external.
**Consequences.** + No extra install, sufficient for our needs. – More verbose than Click, but acceptable.
**Governs:** `src/tasktracker/cli.py`

## ADR-006: Project Structure – src/ Layout

**Context.** We want a clean, installable package.
**Decision.** Use `src/` layout with a package `tasktracker` inside. This is the modern Python recommended structure.
**Alternatives considered.**
1. Flat layout with `tasktracker/` at root – simpler but less clean.
2. No package – just scripts – would make imports messy.
**Consequences.** + Clear separation, easy to install with `pip install -e .`, supports future extension.
**Governs:** Entire project tree.

## ADR-007: Validation Strategy – `__post_init__` + Property Setters

**Context.** Need to enforce priority 1‑5 and non‑past due dates.
**Decision.** Use `__post_init__` for initial validation and `@property.setter` for priority to re‑validate on assignment.
**Alternatives considered.**
1. Only validate in `__post_init__` – then the setter wouldn't protect direct assignment.
2. Use separate validate methods called from outside – less encapsulated.
**Consequences.** + Encapsulation, both creation and modification are safe. – Slightly more code.
**Governs:** `src/tasktracker/models.py`

## ADR-008: Error Handling & Logging

**Context.** The app should not crash on bad inputs or file issues; users need clear feedback.
**Decision.** Use custom exceptions (`ValidationError`, `StorageError`) and a logger for info/warning messages. Catch exceptions in CLI and print user‑friendly messages.
**Alternatives considered.** No logging, just prints – harder to diagnose. Using only `try/except` without custom hierarchy – less expressive.
**Consequences.** + Robust, maintainable. – Slight overhead.
**Governs:** `src/tasktracker/exceptions.py`, `src/tasktracker/storage.py`, `src/tasktracker/cli.py`