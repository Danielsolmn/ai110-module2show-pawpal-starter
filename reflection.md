# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design included four classes: `Pet`, `Task`, `Owner`, and `Scheduler`.

- **Pet** — represents the animal being cared for. It holds basic identifying information: name, species, age, and any freeform notes (e.g., dietary restrictions or medical conditions). Its responsibility is purely data — it does not contain any logic.

- **Task** — represents a single care activity (e.g., morning walk, feeding, medication). It stores the task title, how long it takes (`duration_minutes`), its `priority` (low / medium / high), and an optional `category`. It exposes one behavior: `is_high_priority()`, which encapsulates the priority check so the rest of the system doesn't need to compare strings directly.

- **Owner** — represents the person managing the pet's care. It holds the owner's name, how many minutes they have available in a day (`available_minutes`), any preferences, and a list of their `Pet` objects. The `add_pet()` method keeps the list of pets encapsulated inside the owner.

- **Scheduler** — the only class with real logic. It takes an `Owner` as input and maintains a list of `Task` objects. Its three methods drive the core feature: `add_task()` registers a task, `generate_plan()` selects and orders tasks that fit within the owner's available time, and `explain_plan()` produces a human-readable summary of the chosen schedule and the reasoning behind it.

**b. Design changes**

Yes, the design changed in two meaningful ways after reviewing the skeleton.

The first change was adding `Pet` as an explicit parameter to `Scheduler.__init__`. In the initial UML, `Scheduler` only held a reference to `Owner` and assumed it could reach the pet through `owner.pets`. This created a fragile dependency — the scheduler would need to guess which pet the plan was for, especially since `Owner` supports multiple pets. Making `pet` a direct attribute of `Scheduler` clarified the intent: each scheduler instance is responsible for exactly one pet's daily plan.

The second change was replacing the `priority` string field on `Task` with a `Priority` enum. The original design used a plain string (`"low"`, `"medium"`, `"high"`), which meant a typo like `"High"` or `"urgent"` would silently pass through and break sorting and priority-checking logic. Switching to an `Enum` enforces valid values at the type level and makes comparisons reliable without extra validation code.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: available time, task priority, and task frequency.

Available time is the hard constraint — a task only enters the plan if it fits within the owner's remaining minutes. Priority determines order: HIGH tasks are scheduled first, then MEDIUM, then LOW, so the most important care always gets done even if time runs out. Frequency acts as a filter — tasks marked "daily" or "weekly" are auto-rescheduled after completion, while "as needed" tasks are one-time.

 time and priority mattered most because they reflect real life: a busy owner can't do everything, so the system should help them do the right things first. Frequency came second because recurring tasks like feeding and medication are the ones most likely to be forgotten if not automatically queued up again.

**b. Tradeoffs**

The conflict detector uses an O(n²) pairwise comparison — every task is checked against every other task. A more efficient approach would sort tasks by start time and use a sweep-line algorithm (O(n log n)), which would scale better for large numbers of tasks.

However, I kept the simpler approach for two reasons. First, a real pet owner realistically schedules between 5 and 20 tasks per day. At that scale, the difference between O(n²) and O(n log n) is unmeasurable — the bottleneck is the owner's time, not the algorithm. Second, the pairwise loop is easier to read and verify: `combinations(entries, 2)` directly says "check every unique pair," and the overlap condition `a_start < b_end and b_start < a_end` is a standard interval test that any reader can trace in one pass. A sweep-line would require sorting state and an active-interval set, adding complexity with no practical benefit in this context.

The tradeoff is: simplicity and readability over asymptotic efficiency. That is a reasonable choice when n is small and correctness is more important than raw performance.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools across every phase of the project, but the role shifted depending on the task.

brainstorm methods , 
understand what a code mean ... especially method that takes in different things 



**b. Judgment and verification**

The clearest moment of rejecting an AI suggestion was during the `reschedule()` method. An early suggestion put the rescheduling logic inside `Scheduler` as a standalone method that took both a task and a pet as arguments. I modified this by splitting the responsibility: `reschedule()` lives on `Task` (because it only needs the task's own data to compute the next date), while `mark_task_complete()` lives on `Scheduler` (because finding the right pet to append to requires access to `owner.pets`). The 

I verified the split was correct by asking: "does this method need anything it doesn't already own?" If the answer was no, it belonged on that class.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers six categories of behavior:

- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order, excludes completed tasks, and returns an empty list when no pending tasks exist.
- **Recurrence logic** — daily tasks produce a new task due tomorrow, weekly tasks produce a new task due in 7 days, "as needed" tasks return `None`, and the rescheduled task is appended to the correct pet (not a different one).
- **Conflict detection** — tasks at the same start time are flagged, overlapping windows are flagged, back-to-back tasks that touch but don't overlap are not flagged, completed tasks are excluded from conflict checks, and a single task never conflicts with itself.
- **Invalid input** — `_to_minutes` is tested with valid HH:MM strings and confirmed to raise `ValueError` on malformed input like `"morning"` or `""`. This documents current behavior so future validation can be added to `app.py` at the input boundary.
- **Edge cases** — `generate_plan()` returns an empty list when `available_minutes` is 0; two pets with identically named tasks are tracked independently and completing one does not affect the other; `reschedule()` advances from a past `due_date` correctly rather than defaulting to today.
- **Baseline** — `mark_complete()` correctly sets `completed=True`, and `add_task()` increases the pet's task count.


**b. Confidence**

**★★★★★ (5/5)**

All core scheduling behaviors are tested across happy paths, boundary conditions, and invalid input. The back-to-back conflict boundary, "as needed" recurrence, zero available time, past due dates, and identical task descriptions across pets are all explicitly covered. 

---

## 5. Reflection

**a. What went well**



The conflict detection using itertools.combinations turned out well. Once I understood that lexicographic HH:MM strings sort chronologically without any parsing, the whole approach from _to_minutes to the interval check came together in about ten lines that are easy to explain to anyone.

**b. What you would improve**

add more features ..like subtask 



**c. Key takeaway**

The most important thing I learned is that AI is most useful when you already know what you want. Giving it a more detailed prompt produces more quality code. 


