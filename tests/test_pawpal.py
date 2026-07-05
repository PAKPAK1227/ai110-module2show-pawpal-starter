"""Quick tests for the PawPal+ logic layer."""

from pawpal_system import Pet, Task


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
