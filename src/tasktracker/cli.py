#!/usr/bin/env python3
"""Command-line interface for the Task Tracker using argparse."""
import argparse
import sys
import logging
from datetime import date, datetime
from pathlib import Path
import requests  # Add this with the other imports

from .models import Task, RecurringTask, TaskList
from .storage import load_tasks, save_tasks
from .utils import render_task_list, find_task_by_title, render_tree, count_all_tasks
from .exceptions import TaskTrackerError, ValidationError, StorageError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_STORAGE = "tasks.json"

def parse_date(s: str) -> date:
    """Parse a date in YYYY-MM-DD format."""
    try:
        return date.fromisoformat(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {s}. Use YYYY-MM-DD.")

def parse_priority(s: str) -> int:
    try:
        val = int(s)
        if 1 <= val <= 5:
            return val
        raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError("Priority must be an integer between 1 and 5.")

def load_or_empty(path: str) -> TaskList:
    try:
        return load_tasks(path)
    except StorageError as e:
        logger.error(f"Could not load tasks: {e}")
        return TaskList()  # fallback to empty

def main() -> None:
    parser = argparse.ArgumentParser(description="Task Tracker CLI")
    parser.add_argument("--storage", default=DEFAULT_STORAGE,
                        help=f"Path to JSON storage file (default: {DEFAULT_STORAGE})")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    # ----- add -----
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("--priority", type=parse_priority, default=3,
                            help="Priority 1-5 (1 = highest)")
    add_parser.add_argument("--due", type=parse_date, required=True,
                            help="Due date in YYYY-MM-DD format")
    add_parser.add_argument("--interval", type=int, default=0,
                            help="If >0, create a recurring task with that interval in days")
    add_parser.add_argument("--parent", help="Title of an existing task to add as subtask")

    # ----- list -----
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--all", action="store_true", help="Show all tasks (including done)")
    list_parser.add_argument("--pending", action="store_true", help="Show only pending (default)")
    list_parser.add_argument("--tree", action="store_true", help="Show as tree (recursive)")

    # ----- done -----
    done_parser = subparsers.add_parser("done", help="Mark a task as done")
    done_parser.add_argument("title", help="Title of the task to mark done")

    # ----- show -----
    show_parser = subparsers.add_parser("show", help="Show a task and its subtasks")
    show_parser.add_argument("title", help="Title of the task to show")

    # ----- delete -----
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("title", help="Title of the task to delete")

    

    # ----- weather -----
    weather_parser = subparsers.add_parser("weather", help="Get current weather for a city")
    weather_parser.add_argument("city", help="City name (e.g., Miami)")

    args = parser.parse_args()
    
    # Load tasks
    task_list = load_or_empty(args.storage)

    try:
        if args.command == "add":
            # Create task
            if args.interval > 0:
                task = RecurringTask(args.title, args.priority, args.due, interval_days=args.interval)
            else:
                task = Task(args.title, args.priority, args.due)

            # If parent provided, find and add as subtask
            if args.parent:
                parent = find_task_by_title(task_list.all_tasks(), args.parent)
                if parent is None:
                    print(f"Error: Parent task '{args.parent}' not found.")
                    sys.exit(1)
                parent.subtasks.append(task)
                # Re‑sort parent? Not needed, we sort only flat list.
                print(f"Added subtask '{task.title}' under '{parent.title}'.")
            else:
                task_list.add(task)
                print(f"Added task '{task.title}'.")
            save_tasks(task_list, args.storage)

        elif args.command == "list":
            if args.tree:
                # Show each top‑level task as a tree
                for t in task_list.all_tasks():
                    print(render_tree(t))
                    print()
            else:
                tasks = task_list.all_tasks() if args.all else task_list.pending()
                print(render_task_list(tasks))

        elif args.command == "done":
            task = find_task_by_title(task_list.all_tasks(), args.title)
            if task is None:
                print(f"Error: Task '{args.title}' not found.")
                sys.exit(1)
            task.done = True
            save_tasks(task_list, args.storage)
            print(f"Marked '{args.title}' as done.")

        elif args.command == "show":
            task = find_task_by_title(task_list.all_tasks(), args.title)
            if task is None:
                print(f"Error: Task '{args.title}' not found.")
                sys.exit(1)
            print(render_tree(task))
            print(f"Total subtasks (including itself): {count_all_tasks(task)}")

        elif args.command == "delete":
            # Remove task from flat list; subtasks are not removed automatically.
            # We'll implement a simple removal from the flat list (not recursive).
            # For a more robust version, we'd need a recursive removal.
            # Simpler: we'll just delete the task if it's top‑level.
            # For subtask, we would need to search parent.
            # For brevity, we'll only delete top‑level tasks.
            tasks = task_list.all_tasks()
            for i, t in enumerate(tasks):
                if t.title == args.title:
                    # Check if it has subtasks: warn
                    if t.subtasks:
                        print(f"Warning: Task '{args.title}' has {len(t.subtasks)} subtasks. They will be orphaned (not deleted).")
                    del tasks[i]
                    save_tasks(task_list, args.storage)
                    print(f"Deleted '{args.title}'.")
                    break
            else:
                print(f"Error: Task '{args.title}' not found in top level. (Cannot delete subtasks with this command).")
                sys.exit(1)

        elif args.command == "weather":
            try:
                # Geocode the city
                geo_resp = requests.get(
                    f"https://geocoding-api.open-meteo.com/v1/search?name={args.city}&count=1",
                    timeout=10
                )
                geo_resp.raise_for_status()
                geo_data = geo_resp.json()
                if not geo_data.get("results"):
                    print(f"City '{args.city}' not found.")
                    sys.exit(1)
                
                lat = geo_data["results"][0]["latitude"]
                lon = geo_data["results"][0]["longitude"]
                
                # Get weather
                weather_resp = requests.get(
                    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true",
                    timeout=10
                )
                weather_resp.raise_for_status()
                weather_data = weather_resp.json()
                temp = weather_data["current_weather"]["temperature"]
                print(f"Weather in {args.city}: {temp}°C")
            except requests.RequestException as e:
                print(f"Error fetching weather: {e}")
                sys.exit(1)

    except (ValidationError, StorageError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()