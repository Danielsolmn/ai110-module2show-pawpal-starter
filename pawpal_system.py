from dataclasses import dataclass, field
from enum import Enum
from typing import List


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

    def is_high_priority(self) -> bool:
        return self.priority == Priority.HIGH

    def mark_complete(self) -> None:
        self.completed = True


@dataclass
class Pet:
    """Stores pet details and owns a list of care tasks specific to that pet."""
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """Manages multiple pets and provides unified access to all their tasks."""
    name: str
    available_minutes: int
    preferences: str = ""
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all owned pets."""
        return [task for pet in self.pets for task in pet.get_pending_tasks()]


class Scheduler:
    """The brain of the system — retrieves, organizes, and schedules tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner: Owner = owner

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
