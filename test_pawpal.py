from pawpal_system import Task, Pet, Priority


def test_mark_complete_changes_status():
    """Task completion: mark_complete() should set completed to True."""
    task = Task(description="Morning walk", duration_minutes=30, priority=Priority.HIGH)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Task addition: adding a task to a Pet should increase its task count by 1."""
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(description="Feeding", duration_minutes=10, priority=Priority.MEDIUM))
    assert len(pet.tasks) == 1
