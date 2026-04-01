from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler, Priority

# --- Owner ---
owner = Owner(name="Jordan", available_minutes=90)

# --- Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Tasks for Mochi (added out of order by time) ---
mochi.add_task(Task("Enrichment puzzle", duration_minutes=20, priority=Priority.MEDIUM,
                    frequency="daily",     time="14:00", due_date=date.today()))
mochi.add_task(Task("Morning walk",      duration_minutes=30, priority=Priority.HIGH,
                    frequency="daily",     time="07:30", due_date=date.today()))
mochi.add_task(Task("Feeding",           duration_minutes=10, priority=Priority.HIGH,
                    frequency="daily",     time="08:00", due_date=date.today()))

# --- Tasks for Luna (added out of order by time) ---
# NOTE: Medication starts at 08:30 and Feeding ends at 08:10 — no overlap there.
# Grooming at 11:00 (15 min) and Playtime at 11:10 (20 min) WILL overlap → conflict.
luna.add_task(Task("Playtime",   duration_minutes=20, priority=Priority.LOW,
                   frequency="as needed", time="11:10", due_date=date.today()))
luna.add_task(Task("Medication", duration_minutes=5,  priority=Priority.HIGH,
                   frequency="daily",     time="08:30", due_date=date.today()))
luna.add_task(Task("Grooming",   duration_minutes=15, priority=Priority.MEDIUM,
                   frequency="weekly",    time="11:00", due_date=date.today()))

# --- Register pets with owner ---
owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner)

# --- Conflict detection (runs before the plan so warnings appear first) ---
print("\n=== Conflict Detection ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts detected.")

# --- Original plan ---
print()
print(scheduler.explain_plan())

# --- Sort by time ---
print("\n=== All Pending Tasks Sorted by Time ===")
for task in scheduler.sort_by_time():
    print(f"  {task.time}  {task.description:<25} due={task.due_date}  [{task.frequency}]")

# --- Mark "Morning walk" complete → should auto-schedule tomorrow ---
morning_walk = mochi.tasks[1]
print(f"\n--- Completing: '{morning_walk.description}' (due {morning_walk.due_date}) ---")
next_task = scheduler.mark_task_complete(morning_walk)
if next_task:
    print(f"    Auto-scheduled next: '{next_task.description}' due {next_task.due_date}")

# --- Mark Luna's weekly Grooming complete → should schedule next week ---
grooming = luna.tasks[2]
print(f"\n--- Completing: '{grooming.description}' (due {grooming.due_date}) ---")
next_task = scheduler.mark_task_complete(grooming)
if next_task:
    print(f"    Auto-scheduled next: '{next_task.description}' due {next_task.due_date}")

# --- Mark Playtime complete → 'as needed', should NOT reschedule ---
playtime = luna.tasks[0]
print(f"\n--- Completing: '{playtime.description}' (frequency='{playtime.frequency}') ---")
next_task = scheduler.mark_task_complete(playtime)
if next_task is None:
    print("    No auto-reschedule (as needed task).")

# --- Filter: pending tasks only ---
print("\n=== Pending Tasks After Completions ===")
for task in scheduler.filter_tasks(completed=False):
    print(f"  {task.description:<25} due={task.due_date}")

# --- Filter: completed tasks ---
print("\n=== Completed Tasks ===")
for task in scheduler.filter_tasks(completed=True):
    print(f"  {task.description:<25} was due={task.due_date}")

# --- Filter: Luna's tasks only ---
print("\n=== Luna's Tasks ===")
for task in scheduler.filter_tasks(pet_name="Luna"):
    status = "done" if task.completed else "pending"
    print(f"  {task.description:<25} [{status}]  due={task.due_date}")
