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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector uses an O(n²) pairwise comparison — every task is checked against every other task. A more efficient approach would sort tasks by start time and use a sweep-line algorithm (O(n log n)), which would scale better for large numbers of tasks.

However, I kept the simpler approach for two reasons. First, a real pet owner realistically schedules between 5 and 20 tasks per day. At that scale, the difference between O(n²) and O(n log n) is unmeasurable — the bottleneck is the owner's time, not the algorithm. Second, the pairwise loop is easier to read and verify: `combinations(entries, 2)` directly says "check every unique pair," and the overlap condition `a_start < b_end and b_start < a_end` is a standard interval test that any reader can trace in one pass. A sweep-line would require sorting state and an active-interval set, adding complexity with no practical benefit in this context.

The tradeoff is: simplicity and readability over asymptotic efficiency. That is a reasonable choice when n is small and correctness is more important than raw performance.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
