# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ goes beyond a basic task list with four algorithmic features added to `pawpal_system.py`:

**Sort by time** — `Scheduler.sort_by_time()` returns all pending tasks ordered chronologically. It uses Python's `sorted()` with a lambda key on each task's `"HH:MM"` string. Because the format is zero-padded 24-hour, lexicographic order matches chronological order with no datetime parsing needed.

**Filter tasks** — `Scheduler.filter_tasks(completed, pet_name)` lets you slice the task list by completion status, by pet, or by both at once. Useful for showing only what still needs doing, or auditing a single pet's history.

**Auto-reschedule** — `Task.reschedule()` returns a fresh copy of a task due on its next occurrence using Python's `timedelta`: daily tasks shift by 1 day, weekly tasks by 7 days, and `"as needed"` tasks are not rescheduled. `Scheduler.mark_task_complete()` wires this together — it marks the task done and appends the rescheduled copy to the same pet automatically.

**Conflict detection** — `Scheduler.detect_conflicts()` checks every unique pair of pending tasks with `itertools.combinations` and reports any whose time windows overlap using the interval condition `a_start < b_end and b_start < a_end`. Warnings are returned as strings so the program never crashes — the owner sees the conflict and decides what to do.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
