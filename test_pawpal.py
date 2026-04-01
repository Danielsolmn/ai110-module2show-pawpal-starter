from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Priority, Scheduler, Task, _to_minutes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_owner(available_minutes: int = 120) -> Owner:
    return Owner(name="Alex", available_minutes=available_minutes)


def make_pet(name: str = "Mochi") -> Pet:
    return Pet(name=name, species="dog", age=3)


def make_task(
    description: str = "Walk",
    duration: int = 30,
    priority: Priority = Priority.MEDIUM,
    frequency: str = "daily",
    time: str = "09:00",
    due_date: date | None = None,
) -> Task:
    return Task(
        description=description,
        duration_minutes=duration,
        priority=priority,
        frequency=frequency,
        time=time,
        due_date=due_date or date.today(),
    )


# ---------------------------------------------------------------------------
# Existing tests (kept)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 1. Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() returns tasks ordered earliest → latest."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    pet.add_task(make_task("Evening meds", time="20:00"))
    pet.add_task(make_task("Noon walk",    time="12:00"))
    pet.add_task(make_task("Morning feed", time="08:00"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    times = [t.time for t in sorted_tasks]
    assert times == ["08:00", "12:00", "20:00"]


def test_sort_by_time_excludes_completed_tasks():
    """sort_by_time() only returns pending tasks — completed ones are hidden."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    done = make_task("Done task", time="07:00")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task("Pending task", time="10:00"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    assert len(sorted_tasks) == 1
    assert sorted_tasks[0].time == "10:00"


def test_sort_by_time_empty_when_no_tasks():
    """sort_by_time() returns an empty list when the pet has no tasks."""
    owner = make_owner()
    owner.add_pet(make_pet())

    assert Scheduler(owner).sort_by_time() == []


# ---------------------------------------------------------------------------
# 2. Recurrence logic
# ---------------------------------------------------------------------------

def test_mark_task_complete_creates_next_day_task_for_daily():
    """Completing a daily task adds a new task due tomorrow."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    today = date.today()
    task = make_task("Daily walk", frequency="daily", due_date=today)
    pet.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_mark_task_complete_creates_next_week_task_for_weekly():
    """Completing a weekly task adds a new task due in 7 days."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    today = date.today()
    task = make_task("Weekly bath", frequency="weekly", due_date=today)
    pet.add_task(task)

    next_task = Scheduler(owner).mark_task_complete(task)

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_mark_task_complete_no_reschedule_for_as_needed():
    """'as needed' tasks return None from reschedule and add nothing to the pet."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    task = make_task("Vet visit", frequency="as needed")
    pet.add_task(task)

    next_task = Scheduler(owner).mark_task_complete(task)

    assert next_task is None
    # Only the original (now-completed) task remains
    assert len(pet.tasks) == 1


def test_rescheduled_task_appended_to_correct_pet():
    """The follow-up task is added to the same pet that owned the original."""
    owner = make_owner()
    pet_a = make_pet("Luna")
    pet_b = make_pet("Max")
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    task = make_task("Walk", frequency="daily")
    pet_a.add_task(task)

    Scheduler(owner).mark_task_complete(task)

    # Luna got the follow-up; Max was untouched
    assert len(pet_a.tasks) == 2
    assert len(pet_b.tasks) == 0


# ---------------------------------------------------------------------------
# 3. Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_same_start_time():
    """Two tasks scheduled at the same time should produce a conflict warning."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    pet.add_task(make_task("Feed",  duration=30, time="09:00"))
    pet.add_task(make_task("Walk",  duration=30, time="09:00"))

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "WARNING" in warnings[0]


def test_detect_conflicts_flags_overlapping_tasks():
    """A task starting mid-way through another should be flagged."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    pet.add_task(make_task("Long walk", duration=60, time="09:00"))   # 09:00–10:00
    pet.add_task(make_task("Meds",      duration=10, time="09:30"))   # 09:30–09:40

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1


def test_detect_conflicts_no_warning_for_back_to_back():
    """Tasks ending exactly when the next one starts must NOT conflict."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    pet.add_task(make_task("Walk", duration=30, time="09:00"))   # ends 09:30
    pet.add_task(make_task("Feed", duration=30, time="09:30"))   # starts 09:30

    warnings = Scheduler(owner).detect_conflicts()
    assert warnings == []


def test_detect_conflicts_no_warning_when_no_overlap():
    """Well-separated tasks produce no warnings."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    pet.add_task(make_task("Morning walk", duration=30, time="08:00"))
    pet.add_task(make_task("Evening walk", duration=30, time="18:00"))

    assert Scheduler(owner).detect_conflicts() == []


def test_detect_conflicts_ignores_completed_tasks():
    """Completed tasks should not participate in conflict checking."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)

    done = make_task("Done", duration=60, time="09:00")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task("Active", duration=30, time="09:00"))

    # Only one pending task — no pair to conflict
    assert Scheduler(owner).detect_conflicts() == []


def test_detect_conflicts_empty_when_single_task():
    """A single pending task can never conflict with itself."""
    owner = make_owner()
    pet = make_pet()
    owner.add_pet(pet)
    pet.add_task(make_task("Solo task"))

    assert Scheduler(owner).detect_conflicts() == []


# ---------------------------------------------------------------------------
# 4. Invalid input
# ---------------------------------------------------------------------------

def test_to_minutes_valid_parses_correctly():
    """_to_minutes converts a well-formed HH:MM string to the right integer."""
    assert _to_minutes("00:00") == 0
    assert _to_minutes("08:30") == 510
    assert _to_minutes("23:59") == 1439


def test_to_minutes_invalid_format_raises():
    """_to_minutes raises ValueError when given a non-HH:MM string.

    This documents current behavior — the app does not validate the time
    field before calling _to_minutes, so a bad string crashes detect_conflicts.
    """
    with pytest.raises((ValueError, TypeError)):
        _to_minutes("morning")

    with pytest.raises((ValueError, TypeError)):
        _to_minutes("")


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------

def test_generate_plan_returns_empty_when_no_time_available():
    """generate_plan() returns [] when available_minutes is 0."""
    owner = make_owner(available_minutes=0)
    pet = make_pet()
    owner.add_pet(pet)
    pet.add_task(make_task("Walk", duration=30))

    assert Scheduler(owner).generate_plan() == []


def test_identical_descriptions_across_pets_treated_as_separate_tasks():
    """Two pets with the same task description are tracked independently."""
    owner = make_owner()
    pet_a = make_pet("Luna")
    pet_b = make_pet("Max")
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    pet_a.add_task(make_task("Feeding", time="08:00", frequency="as needed"))
    pet_b.add_task(make_task("Feeding", time="08:00", frequency="as needed"))

    scheduler = Scheduler(owner)

    # Both tasks appear in the sorted view
    assert len(scheduler.sort_by_time()) == 2

    # Completing one does not affect the other
    scheduler.mark_task_complete(pet_a.tasks[0])
    pending = scheduler.filter_tasks(completed=False)
    assert len(pending) == 1
    assert pending[0] in pet_b.tasks


def test_reschedule_works_when_due_date_is_in_the_past():
    """reschedule() correctly advances from a past due_date, not from today."""
    past = date.today() - timedelta(days=10)
    task = make_task("Old walk", frequency="daily", due_date=past)

    next_task = task.reschedule()

    assert next_task is not None
    assert next_task.due_date == past + timedelta(days=1)
