"""Temporary testing ground for PawPal+.

Builds a small owner/pets/tasks setup and prints today's schedule to the
terminal so we can eyeball that the logic layer works. Run with:

    python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_sample_owner() -> Owner:
    """Create an owner with two pets and several tasks of different durations."""
    owner = Owner("Sam", available_minutes=90)

    biscuit = owner.add_pet(Pet("Biscuit", species="Dog", breed="Golden Retriever"))
    biscuit.add_task(Task("Morning walk", duration=30, priority="high"))
    biscuit.add_task(Task("Feeding", duration=10, priority="high"))
    biscuit.add_task(Task("Enrichment play", duration=25, priority="low"))
    biscuit.add_task(Task("Grooming", duration=40, priority="medium", frequency="weekly"))

    whiskers = owner.add_pet(Pet("Whiskers", species="Cat", breed="Tabby"))
    whiskers.add_task(Task("Feeding", duration=5, priority="high"))
    whiskers.add_task(Task("Litter box", duration=10, priority="medium"))

    return owner


def print_schedule(owner: Owner, plan: dict) -> None:
    """Print a clean, readable 'Today's Schedule' block to the terminal."""
    header = f"Today's Schedule for {owner.name}  (budget: {owner.available_minutes} min)"
    print("=" * len(header))
    print(header)
    print("=" * len(header))

    if plan["scheduled"]:
        for entry in plan["scheduled"]:
            task = entry["task"]
            print(
                f"  {entry['start']:%H:%M}-{entry['end']:%H:%M}  "
                f"{task.description:<16} {task.duration:>2} min  "
                f"[{task.priority:<6}] {entry['pet'].name}"
            )
    else:
        print("  (nothing scheduled)")

    if plan["skipped"]:
        print("\nSkipped (ran out of time):")
        for entry in plan["skipped"]:
            task = entry["task"]
            print(f"  - {task.description} ({task.duration} min) for {entry['pet'].name}")

    print(f"\nTotal care time: {plan['total_time']} min")
    print(plan["reasoning"])


def main() -> None:
    owner = build_sample_owner()
    scheduler = Scheduler()
    plan = scheduler.build_plan(owner)
    print_schedule(owner, plan)


if __name__ == "__main__":
    main()
