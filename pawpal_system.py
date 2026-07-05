from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, time, timedelta, datetime

PRIORITY_SCORES = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    """A single care activity for a pet (walk, feeding, meds, grooming, etc.)."""

    description: str
    duration: int
    priority: str = "medium"  # "high" | "medium" | "low"
    frequency: str = "daily"  # "daily" | "weekly" | "once"
    time: str = ""  # scheduled time of day in "HH:MM" (empty = unscheduled)
    due_date: date | None = None
    completed: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def priority_value(self) -> int:
        """Return a sortable score for this task's priority (higher = more important)."""
        return PRIORITY_SCORES.get(self.priority.lower(), 0)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to not done."""
        self.completed = False

    def is_recurring(self) -> bool:
        """Return True if this task repeats (daily or weekly)."""
        return self.frequency in ("daily", "weekly")

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, uncompleted copy due on the next date, or None.

        Daily tasks advance by one day and weekly tasks by one week from the
        current due_date (or today if unset). Non-recurring tasks return None.
        """
        if not self.is_recurring():
            return None
        step = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        base = self.due_date or date.today()
        return Task(
            description=self.description,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            time=self.time,
            due_date=base + step,
        )

    def update(self, **changes) -> None:
        """Update fields on this task (e.g., duration=45, priority='high')."""
        for key, value in changes.items():
            if not hasattr(self, key):
                raise AttributeError(f"Task has no field '{key}'")
            setattr(self, key, value)

    def __str__(self) -> str:
        """Return a one-line, human-readable summary of the task."""
        status = "done" if self.completed else "todo"
        return f"{self.description} ({self.duration} min) [{self.priority}] - {status}"


@dataclass
class Pet:
    """A single animal being cared for, owning its own list of tasks."""

    name: str
    species: str = ""
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> Task:
        """Attach a care task to this pet and return it."""
        self.tasks.append(task)
        return task

    def find_task(self, task_id: str) -> Task | None:
        """Return the task with the given id, or None if not found."""
        return next((t for t in self.tasks if t.id == task_id), None)

    def edit_task(self, task_id: str, **changes) -> Task:
        """Update an existing task's fields by id."""
        task = self.find_task(task_id)
        if task is None:
            raise KeyError(f"No task with id '{task_id}' on pet '{self.name}'")
        task.update(**changes)
        return task

    def remove_task(self, task_id: str) -> bool:
        """Delete a task by id. Returns True if a task was removed."""
        task = self.find_task(task_id)
        if task is None:
            return False
        self.tasks.remove(task)
        return True

    def list_tasks(self) -> list[Task]:
        """Return all tasks belonging to this pet."""
        return list(self.tasks)

    def pending_tasks(self) -> list[Task]:
        """Return only the tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """A pet owner who manages one or more pets and their care time budget."""

    name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> Pet:
        """Register a new pet and return it."""
        self.pets.append(pet)
        return pet

    def find_pet(self, name: str) -> Pet | None:
        """Return the pet with the given name, or None if not found."""
        return next((p for p in self.pets if p.name == name), None)

    def remove_pet(self, name: str) -> bool:
        """Remove a pet by name. Returns True if a pet was removed."""
        pet = self.find_pet(name)
        if pet is None:
            return False
        self.pets.remove(pet)
        return True

    def set_available_time(self, minutes: int) -> None:
        """Update how much care time is available today."""
        if minutes < 0:
            raise ValueError("available_minutes cannot be negative")
        self.available_minutes = minutes

    def set_preference(self, key: str, value) -> None:
        """Record a care preference (e.g., 'walks_before' -> '12:00')."""
        self.preferences[key] = value

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all pets, paired with its pet."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every not-yet-completed task across all pets, paired with its pet."""
        return [(pet, task) for pet, task in self.all_tasks() if not task.completed]


class Scheduler:
    """The brain: gathers tasks across an owner's pets, organizes them by
    priority, and fits them into the available time to produce a daily plan.

    A plan is a dict with keys:
        scheduled  - list of {start, end, pet, task}
        skipped    - list of {pet, task, reason}
        total_time - minutes of care scheduled
        reasoning  - human-readable explanation of the plan
    """

    def __init__(self, strategy: str = "priority", day_start: time = time(8, 0)) -> None:
        """Create a scheduler with a sort strategy and a day start time."""
        self.strategy = strategy
        self.day_start = day_start

    def sort_tasks(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Order (pet, task) pairs: highest priority first, then shortest first
        so more tasks can fit in the available time."""
        if self.strategy == "duration":
            key = lambda pt: (pt[1].duration, -pt[1].priority_value())
        else:
            key = lambda pt: (-pt[1].priority_value(), pt[1].duration)
        return sorted(pairs, key=key)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by their "HH:MM" time; unscheduled tasks last.

        Zero-padded "HH:MM" strings sort correctly with plain string
        comparison, so the lambda key just falls back to "99:99" for tasks
        with no time set.
        """
        return sorted(tasks, key=lambda t: t.time or "99:99")

    def filter_tasks(
        self,
        owner: Owner,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks for an owner, optionally filtered by pet and/or status.

        Pass pet_name to keep only that pet's tasks, and completed=True/False
        to keep only done/not-done tasks. Omitting a filter leaves it open.
        """
        result = []
        for pet, task in owner.all_tasks():
            if pet_name is not None and pet.name != pet_name:
                continue
            if completed is not None and task.completed != completed:
                continue
            result.append(task)
        return result

    def build_plan(self, owner: Owner, available_minutes: int | None = None) -> dict:
        """Build a daily plan for the owner within the available time budget.

        Greedily walks tasks in sorted order, placing each one that still fits
        and skipping the rest. Falls back to the owner's own available_minutes
        when no budget is passed in.
        """
        budget = owner.available_minutes if available_minutes is None else available_minutes

        ordered = self.sort_tasks(owner.pending_tasks())
        scheduled: list[dict] = []
        skipped: list[dict] = []
        remaining = budget
        cursor = datetime.combine(datetime.today(), self.day_start)

        for pet, task in ordered:
            if task.duration <= remaining:
                start = cursor.time()
                cursor += timedelta(minutes=task.duration)
                scheduled.append(
                    {"start": start, "end": cursor.time(), "pet": pet, "task": task}
                )
                remaining -= task.duration
            else:
                skipped.append(
                    {"pet": pet, "task": task, "reason": "not enough time left"}
                )

        total_time = budget - remaining
        reasoning = (
            f"Sorted {len(ordered)} pending task(s) by {self.strategy}. "
            f"Scheduled {len(scheduled)} using {total_time} of {budget} min; "
            f"skipped {len(skipped)} that did not fit."
        )
        return {
            "scheduled": scheduled,
            "skipped": skipped,
            "total_time": total_time,
            "reasoning": reasoning,
        }

    def mark_task_complete(self, owner: Owner, task_id: str) -> Task | None:
        """Mark a task done by id; if it recurs, queue and return its next copy.

        Searches every pet, marks the matching task complete, and for daily or
        weekly tasks adds a fresh next-occurrence to the same pet so the chore
        reappears. Returns the new task (or None if nothing recurred/matched).
        """
        for pet, task in owner.all_tasks():
            if task.id == task_id:
                task.mark_complete()
                upcoming = task.next_occurrence()
                if upcoming is not None:
                    pet.add_task(upcoming)
                return upcoming
        return None

    def detect_conflicts(self, owner: Owner) -> list[str]:
        """Return warning strings for tasks that share the same time slot.

        Lightweight, non-fatal check: groups scheduled tasks by their "HH:MM"
        time and reports any slot holding more than one task (across the same
        or different pets). Tasks with no time set are ignored.
        """
        by_time: dict[str, list[tuple[Pet, Task]]] = {}
        for pet, task in owner.all_tasks():
            if task.time:
                by_time.setdefault(task.time, []).append((pet, task))

        warnings = []
        for slot, items in sorted(by_time.items()):
            if len(items) > 1:
                names = ", ".join(f"{task.description} ({pet.name})" for pet, task in items)
                warnings.append(f"Conflict at {slot}: {names}")
        return warnings

    def format_plan(self, plan: dict) -> str:
        """Render a plan as readable text for a CLI or the Streamlit UI."""
        lines: list[str] = []
        for entry in plan["scheduled"]:
            t = entry["task"]
            lines.append(
                f"  {entry['start']:%H:%M} - {t.description} "
                f"({t.duration} min) for {entry['pet'].name} [{t.priority}]"
            )
        for entry in plan["skipped"]:
            t = entry["task"]
            lines.append(f"  (skipped) {t.description} for {entry['pet'].name} - {entry['reason']}")
        lines.append("")
        lines.append(plan["reasoning"])
        return "\n".join(lines)
