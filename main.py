from pawpal_system import Task, Pet, Owner, Scheduler, Priority

# --- Owner ---
owner = Owner(name="Jordan", available_minutes=90)

# --- Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Tasks for Mochi ---
mochi.add_task(Task("Morning walk",      duration_minutes=30, priority=Priority.HIGH))
mochi.add_task(Task("Feeding",           duration_minutes=10, priority=Priority.HIGH))
mochi.add_task(Task("Enrichment puzzle", duration_minutes=20, priority=Priority.MEDIUM))

# --- Tasks for Luna ---
luna.add_task(Task("Grooming",           duration_minutes=15, priority=Priority.MEDIUM))
luna.add_task(Task("Medication",         duration_minutes=5,  priority=Priority.HIGH))
luna.add_task(Task("Playtime",           duration_minutes=20, priority=Priority.LOW))

# --- Register pets with owner ---
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Run scheduler ---
scheduler = Scheduler(owner)
print(scheduler.explain_plan())
