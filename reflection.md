# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

Based on the PawPal+ scenario, a user should be able to perform these three core actions:

1. **Add a pet (and owner) profile** — The user enters basic owner information and creates a pet with details like name, species/breed, and any care preferences. This gives the app the context it needs to plan care around a specific animal.
2. **Add or edit a care task** — The user records tasks such as walks, feeding, medications, enrichment, or grooming. Each task carries at least a duration and a priority (and can be edited later) so the scheduler knows how long it takes and how important it is.
3. **Generate and view today's daily plan** — The user asks PawPal+ to build a daily schedule from the current tasks, respecting constraints like available time and priority. The app then displays the resulting plan clearly and, ideally, explains why it ordered things the way it did.

**a. Initial design**

My design settled on four classes:

- **Task** — one care activity: description, duration (time), priority, frequency, and completion status.
- **Pet** — a single animal (name, species, breed) that owns its list of tasks.
- **Owner** — the user; holds available care time and preferences, manages multiple pets, and exposes all their tasks in one place.
- **Scheduler** — the "brain" that gathers tasks across all of the owner's pets, sorts them by priority, and fits them into the available time to build a daily plan.

Relationships: an Owner has many Pets, each Pet has many Tasks, and the Scheduler reads the Owner to organize Tasks into a plan.

**b. Design changes**

- **Added an `id` to Task.** The review flagged that `Pet.edit_task(task_id)` and `remove_task(task_id)` referenced an identifier that didn't exist. I added an auto-generated `id` so tasks can be found and edited/removed reliably.
- **Renamed CareTask → Task and dropped DailyPlan.** I simplified to four classes. Instead of a separate `DailyPlan` object, `Scheduler.build_plan` returns a lightweight dict (scheduled, skipped, total_time, reasoning), which was enough for the UI and easier to test.
- **Made the Scheduler work across pets.** Rather than duplicating `available_minutes`, the `Scheduler` reads `Owner.pending_tasks()` (which returns `(pet, task)` pairs) so tasks stay linked to their pet across the whole household, and the time budget comes from the owner at plan time.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
