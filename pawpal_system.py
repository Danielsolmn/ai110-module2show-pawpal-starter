from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from itertools import combinations
from typing import List, Optional


class Priority(Enum):
    """Valid priority levels for a Task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """Represents a single care activity with its description, duration, frequency, and completion status."""
    description: str
    duration_minutes: int
    priority: Priority
    frequency: str = "daily"
    completed: bool = False
    time: str = "09:00"  # Scheduled time in "HH:MM" format
    due_date: date = field(default_factory=date.today)

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is HIGH."""
        return self.priority == Priority.HIGH

    def mark_complete(self) -> None:
        """Mark this task as completed by setting completed to True."""
        self.completed = True

    def reschedule(self) -> Optional["Task"]:
        """Return a new Task due on the next occurrence based on this task's frequency.

        Uses timedelta to calculate the next due_date:
        - 'daily'  → due_date + 1 day
        - 'weekly' → due_date + 7 days
        - 'as needed' → returns None (no automatic rescheduling)

        The returned Task is a fresh copy with completed=False so it
        appears in future pending-task queries.

        Returns:
            A new Task scheduled for the next occurrence, or None if the
            task frequency does not support automatic rescheduling.
        """
        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(weeks=1)
        else:
            return None  # "as needed" tasks are not auto-rescheduled
        return Task(
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            time=self.time,
            due_date=next_due,
        )


@dataclass
class Pet:
    """Stores pet details and owns a list of care tasks specific to that pet."""
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed yet."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """Manages multiple pets and provides unified access to all their tasks."""
    name: str
    available_minutes: int
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Append a Pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return all pending tasks across every pet this owner has."""
        return [task for pet in self.pets for task in pet.get_pending_tasks()]


def _to_minutes(time_str: str) -> int:
    """Convert a 'HH:MM' string to total minutes since midnight.

    Used internally by detect_conflicts to compare task start/end times
    as plain integers, avoiding datetime parsing overhead.

    Args:
        time_str: A time string in 'HH:MM' 24-hour format (e.g. '08:30').

    Returns:
        The number of minutes elapsed since midnight (e.g. '08:30' → 510).
    """
    hours, mins = time_str.split(":")
    return int(hours) * 60 + int(mins)


class Scheduler:
    """The brain of the system — retrieves, organizes, and schedules tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner: Owner = owner

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for any pending tasks whose time windows overlap.

        Checks every unique pair of pending tasks across all pets using
        itertools.combinations. Two tasks conflict when their scheduled
        windows overlap, tested with the standard interval condition:
            a_start < b_end  AND  b_start < a_end

        This is an O(n²) pairwise scan — acceptable because a realistic
        daily schedule contains a small, bounded number of tasks.

        Returns:
            A list of human-readable warning strings, one per conflicting
            pair. Returns an empty list when no conflicts are found.
        """
        # Build a flat list of (pet_name, task) for all pending tasks
        entries = [
            (pet.name, task)
            for pet in self.owner.pets
            for task in pet.get_pending_tasks()
        ]

        warnings = []
        for (pet_a, task_a), (pet_b, task_b) in combinations(entries, 2):
            a_start = _to_minutes(task_a.time)
            a_end   = a_start + task_a.duration_minutes
            b_start = _to_minutes(task_b.time)
            b_end   = b_start + task_b.duration_minutes
            if a_start < b_end and b_start < a_end:
                warnings.append(
                    f"WARNING: '{task_a.description}' ({pet_a}, {task_a.time}, "
                    f"{task_a.duration_minutes} min) overlaps "
                    f"'{task_b.description}' ({pet_b}, {task_b.time}, "
                    f"{task_b.duration_minutes} min)"
                )
        return warnings

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and automatically schedule its next occurrence.

        Calls task.mark_complete() to set completed=True, then calls
        task.reschedule() to produce the follow-up Task. If a next
        occurrence exists (i.e. frequency is 'daily' or 'weekly'), it is
        appended to the same pet's task list so it will appear in future
        pending-task queries.

        Args:
            task: The Task to mark as done. Must already belong to one of
                  the owner's pets.

        Returns:
            The newly created follow-up Task, or None if the task's
            frequency is 'as needed' and no reschedule was created.
        """
        task.mark_complete()
        next_task = task.reschedule()
        if next_task is not None:
            for pet in self.owner.pets:
                if task in pet.tasks:
                    pet.add_task(next_task)
                    break
        return next_task

    def generate_plan(self) -> List[Task]:
        """Select and order tasks that fit within the owner's available time."""
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        sorted_tasks = sorted(self.owner.get_all_tasks(), key=lambda t: priority_order[t.priority])

        plan = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.owner.available_minutes:
                plan.append(task)
                time_used += task.duration_minutes
        return plan

    def sort_by_time(self) -> List[Task]:
        """Return all pending tasks sorted chronologically by their scheduled time.

        Uses Python's built-in sorted() with a lambda key that extracts
        each task's 'HH:MM' time string. Because the format is zero-padded
        and 24-hour, lexicographic string order matches chronological order
        — no datetime parsing is required.

        Returns:
            A new list of pending Tasks ordered from earliest to latest
            scheduled time. The original task lists are not modified.
        """
        all_tasks = self.owner.get_all_tasks()
        return sorted(all_tasks, key=lambda t: t.time)

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> List[Task]:
        """Return tasks filtered by completion status, pet name, or both.

        Both parameters are optional. Passing neither returns all tasks
        across all pets. Passing one filters by that dimension only.
        Passing both applies both filters together (AND logic).

        The pet_name match is case-insensitive so 'luna' and 'Luna'
        return the same results.

        Args:
            completed: If True, return only completed tasks. If False,
                       return only pending tasks. If None, include both.
            pet_name:  If provided, restrict results to tasks belonging
                       to the pet with this name. If None, include all pets.

        Returns:
            A list of Tasks matching all supplied filters.
        """
        results = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    def explain_plan(self) -> str:
        """Return a human-readable summary of the plan and reasoning."""
        plan = self.generate_plan()
        if not plan:
            return "No tasks fit within the available time."

        lines = ["=" * 40,
                 f"  Today's Schedule for {self.owner.name}",
                 "=" * 40]

        time_used = 0
        for task in plan:
            tag = "(!)" if task.is_high_priority() else "   "
            lines.append(f"{tag} {task.description:<30} {task.duration_minutes} min  [{task.priority.value}]")
            time_used += task.duration_minutes

        lines.append("-" * 40)
        lines.append(f"    Total: {time_used} / {self.owner.available_minutes} min available")
        lines.append("=" * 40)
        return "\n".join(lines)
