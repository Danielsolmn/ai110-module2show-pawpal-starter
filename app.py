import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


# --- Persistent state: initialize once, survive every rerun ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_minutes=60)

if "pets" not in st.session_state:
    st.session_state.pets = []

st.title("🐾 PawPal+")

# ── Owner Setup ───────────────────────────────────────────────
st.subheader("Owner Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value=st.session_state.owner.name)
with col2:
    available = st.number_input("Available minutes today", min_value=10, max_value=480,
                                value=st.session_state.owner.available_minutes)

if st.button("Save owner info"):
    st.session_state.owner.name = owner_name
    st.session_state.owner.available_minutes = available
    st.success(f"Saved! Hi {owner_name}, you have {available} min today.")

st.divider()

# ── Add a Pet ─────────────────────────────────────────────────
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=30, value=1)

if st.button("Add pet"):
    if pet_name.strip():
        new_pet = Pet(name=pet_name.strip(), species=species, age=age)
        st.session_state.owner.add_pet(new_pet)
        st.session_state.pets = st.session_state.owner.pets
        st.success(f"{pet_name} added!")
    else:
        st.warning("Please enter a pet name.")

if st.session_state.owner.pets:
    st.write("**Your pets:**", ", ".join(p.name for p in st.session_state.owner.pets))

st.divider()

# ── Add a Task ────────────────────────────────────────────────
st.subheader("Add a Task")

if not st.session_state.owner.pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    pet_names = [p.name for p in st.session_state.owner.pets]
    col1, col2 = st.columns(2)
    with col1:
        selected_pet = st.selectbox("Assign task to", pet_names)
    with col2:
        task_desc = st.text_input("Task description", value="Morning walk")

    col3, col4, col5, col6 = st.columns(4)
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col4:
        priority_str = st.selectbox("Priority", ["high", "medium", "low"])
    with col5:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
    with col6:
        task_time = st.text_input("Time (HH:MM)", value="09:00")

    if st.button("Add task"):
        if task_desc.strip():
            target_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet)
            new_task = Task(
                description=task_desc.strip(),
                duration_minutes=int(duration),
                priority=Priority(priority_str),
                frequency=frequency,
                time=task_time.strip(),
            )
            target_pet.add_task(new_task)
            st.success(f"Task '{task_desc}' added to {selected_pet}.")
        else:
            st.warning("Please enter a task description.")

    # Show current tasks per pet
    for pet in st.session_state.owner.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks:**")
            st.table([
                {
                    "Task": t.description,
                    "Time": t.time,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.value,
                    "Frequency": t.frequency,
                    "Done": "✅" if t.completed else "⬜",
                }
                for t in pet.tasks
            ])

st.divider()

# ── Conflict Check ────────────────────────────────────────────
st.subheader("⚠️ Schedule Conflicts")

if not st.session_state.owner.pets:
    st.info("Add pets and tasks to check for conflicts.")
else:
    scheduler = Scheduler(st.session_state.owner)
    conflicts = scheduler.detect_conflicts()

    if not conflicts:
        st.success("No conflicts found — your schedule looks clean!")
    else:
        st.error(
            f"**{len(conflicts)} conflict{'s' if len(conflicts) > 1 else ''} detected.**  "
            "Two or more tasks overlap in time. Adjust a task's start time or duration to resolve."
        )
        for warning in conflicts:
            # Strip the leading "WARNING: " prefix for a cleaner display
            message = warning.replace("WARNING: ", "")
            st.warning(f"🔴 {message}")

st.divider()

# ── Tasks Sorted by Time ──────────────────────────────────────
st.subheader("🕐 Today's Tasks by Time")

if not st.session_state.owner.pets:
    st.info("Add pets and tasks to see a sorted view.")
else:
    scheduler = Scheduler(st.session_state.owner)
    sorted_tasks = scheduler.sort_by_time()

    if not sorted_tasks:
        st.info("No pending tasks to display.")
    else:
        st.caption(f"{len(sorted_tasks)} pending task(s), sorted chronologically.")
        st.table([
            {
                "Time": t.time,
                "Task": t.description,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority.value.upper(),
                "Frequency": t.frequency,
            }
            for t in sorted_tasks
        ])

st.divider()

# ── Generate Schedule ─────────────────────────────────────────
st.subheader("Generate Today's Schedule")

if st.button("Generate schedule"):
    if not st.session_state.owner.name:
        st.warning("Please save your owner info first.")
    elif not st.session_state.owner.pets:
        st.warning("Add at least one pet before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner)

        # Surface conflicts at the top of the plan as well
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning(
                f"⚠️ Heads up: {len(conflicts)} time conflict(s) exist in your task list. "
                "The plan below selects by priority — consider fixing conflicts above."
            )

        plan = scheduler.generate_plan()
        if plan:
            total = sum(t.duration_minutes for t in plan)
            st.success(
                f"Here's your plan for today — {total} of {st.session_state.owner.available_minutes} min used."
            )
            st.table([
                {
                    "Task": t.description,
                    "Time": t.time,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.value.upper(),
                    "Frequency": t.frequency,
                }
                for t in plan
            ])
        else:
            st.warning("No tasks fit within your available time.")
