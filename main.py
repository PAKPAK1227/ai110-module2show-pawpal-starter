"""Temporary testing ground for PawPal+.

Builds a small owner/pets/tasks setup and exercises the scheduling logic in
the terminal so we can eyeball that the logic layer works. Run with:

    python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_sample_owner() -> Owner:
    """Create an owner with two pets and tasks added out of time order."""
    owner = Owner("Sam", available_minutes=120)

    biscuit = owner.add_pet(Pet("Biscuit", species="Dog", breed="Golden Retriever"))
    # Added out of order on purpose so sort_by_time has something to fix.
    biscuit.add_task(Task("Morning walk", duration=30, priority="high", time="08:00"))
    biscuit.add_task(Task("Feeding", duration=10, priority="high", time="07:30"))
    biscuit.add_task(Task("Enrichment play", duration=25, priority="low", time="17:00"))
    biscuit.add_task(Task("Grooming", duration=40, priority="medium", frequency="weekly", time="12:00"))

    whiskers = owner.add_pet(Pet("Whiskers", species="Cat", breed="Tabby"))
    whiskers.add_task(Task("Feeding", duration=5, priority="high", time="07:30"))
    whiskers.add_task(Task("Litter box", duration=10, priority="medium", time="18:00"))

    return owner


def print_schedule(owner: Owner, plan: dict) -> None:
    """Print a clean, readable 'Today's Schedule' block to the terminal."""
    header = f"Today's Schedule for {owner.name}  (budget: {owner.available_minutes} min)"
    print("=" * len(header))
    print(header)
    print("=" * len(header))

    for entry in plan["scheduled"]:
        task = entry["task"]
        print(
            f"  {entry['start']:%H:%M}-{entry['end']:%H:%M}  "
            f"{task.description:<16} {task.duration:>2} min  "
            f"[{task.priority:<6}] {entry['pet'].name}"
        )
    if plan["skipped"]:
        print("\nSkipped (ran out of time):")
        for entry in plan["skipped"]:
            task = entry["task"]
            print(f"  - {task.description} ({task.duration} min) for {entry['pet'].name}")
    print(f"\nTotal care time: {plan['total_time']} min")
    print(plan["reasoning"])


def demo_sorting_and_filtering(owner: Owner, scheduler: Scheduler) -> None:
    """Show sort_by_time and filter_tasks working against the sample data."""
    print("\nAgenda sorted by time")
    print("-" * 21)
    all_tasks = [task for _pet, task in owner.all_tasks()]
    for task in scheduler.sort_by_time(all_tasks):
        stamp = task.time or "--:--"
        print(f"  {stamp}  {task.description}")

    print("\nFilter: only Biscuit's tasks")
    print("-" * 28)
    for task in scheduler.filter_tasks(owner, pet_name="Biscuit"):
        print(f"  {task.time or '--:--'}  {task.description}")

    print("\nFilter: only unfinished tasks")
    print("-" * 29)
    for task in scheduler.filter_tasks(owner, completed=False):
        print(f"  {task.time or '--:--'}  {task.description}")


def demo_conflicts(owner: Owner, scheduler: Scheduler) -> None:
    """Show conflict detection: both pets are fed at 07:30 in the sample data."""
    print("\nConflict check")
    print("-" * 14)
    conflicts = scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"  ⚠️  {warning}")
    else:
        print("  No conflicts found.")


def demo_recurring(owner: Owner, scheduler: Scheduler) -> None:
    """Show that completing a recurring task queues its next occurrence."""
    print("\nRecurring tasks")
    print("-" * 15)
    biscuit = owner.find_pet("Biscuit")
    grooming = next(t for t in biscuit.tasks if t.description == "Grooming")
    print(f"  Before: Biscuit has {len(biscuit.tasks)} tasks; completing weekly '{grooming.description}'")
    upcoming = scheduler.mark_task_complete(owner, grooming.id)
    print(f"  After:  Biscuit has {len(biscuit.tasks)} tasks; next '{upcoming.description}' due {upcoming.due_date}")


def main() -> None:
    owner = build_sample_owner()
    scheduler = Scheduler()

    print_schedule(owner, scheduler.build_plan(owner))
    demo_sorting_and_filtering(owner, scheduler)
    demo_conflicts(owner, scheduler)
    demo_recurring(owner, scheduler)


if __name__ == "__main__":
    main()
