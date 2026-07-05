"""Tests for the PawPal+ logic layer.

Covers the core behaviors (task completion, adding tasks, sorting, filtering,
recurrence, conflict detection, priority planning) plus a few edge cases such
as pets with no tasks and non-recurring tasks.
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


# --- Basic task / pet behavior ----------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task's completed status to True."""
    task = Task("Morning walk", duration=30, priority="high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet("Biscuit", species="Dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", duration=10, priority="high"))

    assert len(pet.tasks) == 1


# --- Sorting -----------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() orders tasks by their HH:MM time, earliest first."""
    scheduler = Scheduler()
    tasks = [
        Task("Evening walk", duration=30, time="18:00"),
        Task("Feeding", duration=10, time="07:30"),
        Task("Lunch", duration=15, time="12:00"),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert [t.time for t in ordered] == ["07:30", "12:00", "18:00"]


def test_sort_by_time_places_unscheduled_tasks_last():
    """Tasks with no time set sort after all timed tasks."""
    scheduler = Scheduler()
    tasks = [
        Task("Unscheduled", duration=10),  # time defaults to ""
        Task("Feeding", duration=10, time="07:30"),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert ordered[0].description == "Feeding"
    assert ordered[-1].description == "Unscheduled"


# --- Filtering ---------------------------------------------------------------

def test_filter_tasks_by_pet_name():
    """filter_tasks() returns only the named pet's tasks."""
    owner = Owner("Sam")
    biscuit = owner.add_pet(Pet("Biscuit"))
    whiskers = owner.add_pet(Pet("Whiskers"))
    biscuit.add_task(Task("Walk", duration=30))
    whiskers.add_task(Task("Litter box", duration=10))

    result = Scheduler().filter_tasks(owner, pet_name="Biscuit")

    assert [t.description for t in result] == ["Walk"]


def test_filter_tasks_by_completion_status():
    """filter_tasks(completed=False) returns only unfinished tasks."""
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Biscuit"))
    done = pet.add_task(Task("Feeding", duration=10))
    pet.add_task(Task("Walk", duration=30))
    done.mark_complete()

    pending = Scheduler().filter_tasks(owner, completed=False)

    assert [t.description for t in pending] == ["Walk"]


# --- Recurrence --------------------------------------------------------------

def test_completing_daily_task_creates_next_days_task():
    """Completing a daily task queues a fresh copy due the following day."""
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Biscuit"))
    task = pet.add_task(Task("Feeding", duration=10, frequency="daily", time="07:30"))

    upcoming = Scheduler().mark_task_complete(owner, task.id)

    assert task.completed is True
    assert len(pet.tasks) == 2  # original + next occurrence
    assert upcoming is not None
    assert upcoming.completed is False
    assert upcoming.due_date == date.today() + timedelta(days=1)


def test_completing_weekly_task_advances_one_week():
    """A weekly task's next occurrence is due seven days later."""
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Biscuit"))
    task = pet.add_task(Task("Grooming", duration=40, frequency="weekly"))

    upcoming = Scheduler().mark_task_complete(owner, task.id)

    assert upcoming.due_date == date.today() + timedelta(weeks=1)


def test_non_recurring_task_does_not_regenerate():
    """A one-off task does not spawn a new occurrence when completed."""
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Biscuit"))
    task = pet.add_task(Task("Vet visit", duration=60, frequency="once"))

    upcoming = Scheduler().mark_task_complete(owner, task.id)

    assert upcoming is None
    assert len(pet.tasks) == 1


# --- Conflict detection ------------------------------------------------------

def test_detect_conflicts_flags_duplicate_times():
    """Two tasks scheduled at the same time produce a conflict warning."""
    owner = Owner("Sam")
    biscuit = owner.add_pet(Pet("Biscuit"))
    whiskers = owner.add_pet(Pet("Whiskers"))
    biscuit.add_task(Task("Feeding", duration=10, time="07:30"))
    whiskers.add_task(Task("Feeding", duration=5, time="07:30"))

    warnings = Scheduler().detect_conflicts(owner)

    assert len(warnings) == 1
    assert "07:30" in warnings[0]


def test_detect_conflicts_returns_empty_when_times_differ():
    """No conflict is reported when all task times are distinct."""
    owner = Owner("Sam")
    pet = owner.add_pet(Pet("Biscuit"))
    pet.add_task(Task("Feeding", duration=10, time="07:30"))
    pet.add_task(Task("Walk", duration=30, time="08:00"))

    assert Scheduler().detect_conflicts(owner) == []


# --- Priority planning & edge cases -----------------------------------------

def test_build_plan_skips_tasks_that_exceed_budget():
    """Low-priority tasks are skipped once the time budget is used up."""
    owner = Owner("Sam", available_minutes=20)
    pet = owner.add_pet(Pet("Biscuit"))
    pet.add_task(Task("Walk", duration=20, priority="high"))
    pet.add_task(Task("Play", duration=15, priority="low"))

    plan = Scheduler().build_plan(owner)

    scheduled = [e["task"].description for e in plan["scheduled"]]
    skipped = [e["task"].description for e in plan["skipped"]]
    assert scheduled == ["Walk"]
    assert skipped == ["Play"]


def test_build_plan_with_no_tasks_is_empty_and_safe():
    """An owner with a pet but no tasks yields an empty, non-crashing plan."""
    owner = Owner("Sam", available_minutes=60)
    owner.add_pet(Pet("Biscuit"))

    plan = Scheduler().build_plan(owner)

    assert plan["scheduled"] == []
    assert plan["skipped"] == []
    assert plan["total_time"] == 0
