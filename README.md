# PawPal+ — Pet Care Scheduler

PawPal+ is a Streamlit app that helps pet owners plan and manage daily care tasks for one or more pets. It generates a prioritized schedule, sorts tasks by time, detects conflicts, and automatically reschedules recurring activities.

---

## Features

**Multi-pet support**
Add as many pets as you need. Each pet has its own task list, and the scheduler works across all of them at once.

**Priority-based scheduling**
Tasks are ranked HIGH, MEDIUM, or LOW. When generating a daily plan, the scheduler fills your available time with the most important tasks first.

**Sorting by time**
View all pending tasks in chronological order using `Scheduler.sort_by_time()`. Tasks are sorted by their `HH:MM` scheduled time so you always know what comes next.

**Conflict warnings**
`Scheduler.detect_conflicts()` checks every pair of pending tasks and flags any whose time windows overlap. Warnings are displayed in the app so you can adjust times without the program crashing.

**Daily recurrence**
When you mark a task complete, `Task.reschedule()` automatically creates the next occurrence using Python's `timedelta`. Daily tasks reappear tomorrow; weekly tasks reappear in 7 days. Tasks set to "as needed" are not rescheduled.

**Filtering**
`Scheduler.filter_tasks()` lets you view tasks by completion status, by pet name, or both — useful for checking what still needs doing or reviewing a single pet's history.

**Human-readable plan summary**
`Scheduler.explain_plan()` produces a formatted schedule showing each task, its duration, and priority tag, plus a total time used vs. available.

---

## Project structure

```
pawpal_system.py   Core logic: Task, Pet, Owner, Scheduler classes
app.py             Streamlit UI
main.py            CLI demo script — runs sorting, filtering, conflict detection, and recurrence in the terminal
reflection.md      Design decisions and tradeoffs
uml_final.png      Final UML class diagram
```

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the CLI demo

```bash
python3 main.py
```

### Run the tests

```bash
python -m pytest test_pawpal.py -v
```

---

## How it works

1. Enter your name and how many minutes you have available today.
2. Add one or more pets with their name, species, and age.
3. Add care tasks to each pet — set a description, scheduled time, duration, priority, and frequency.
4. Check the conflict panel to see if any tasks overlap.
5. Click **Generate schedule** to get a prioritized plan that fits within your time budget.
6. Mark tasks complete — recurring ones are automatically rescheduled for the next occurrence.
