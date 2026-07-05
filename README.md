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

## 🖥️ Sample Output

Terminal output from running the logic layer with `python main.py`:

```
==========================================
Today's Schedule for Sam  (budget: 90 min)
==========================================
  08:00-08:05  Feeding           5 min  [high  ] Whiskers
  08:05-08:15  Feeding          10 min  [high  ] Biscuit
  08:15-08:45  Morning walk     30 min  [high  ] Biscuit
  08:45-08:55  Litter box       10 min  [medium] Whiskers
  08:55-09:20  Enrichment play  25 min  [low   ] Biscuit

Skipped (ran out of time):
  - Grooming (40 min) for Biscuit

Total care time: 80 min
Sorted 6 pending task(s) by priority. Scheduled 5 using 80 of 90 min; skipped 1 that did not fit.
```

## 🧪 Testing PawPal+

Run the full suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`, 13 tests):

- **Task & pet basics** — marking a task complete flips its status; adding a task grows the pet's task list.
- **Sorting** — `sort_by_time()` returns tasks in chronological `HH:MM` order and pushes unscheduled tasks last.
- **Filtering** — `filter_tasks()` narrows by pet name and by completion status.
- **Recurrence** — completing a daily task queues a copy due the next day; a weekly task advances one week; a one-off task does not regenerate.
- **Conflict detection** — `detect_conflicts()` flags two tasks sharing a time slot and stays silent when times differ.
- **Priority planning & edge cases** — `build_plan()` skips tasks that exceed the time budget, and an owner with no tasks produces an empty, non-crashing plan.

Successful run:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-9.1.0, pluggy-1.6.0
collected 13 items

tests/test_pawpal.py .............                                       [100%]

============================== 13 passed in 0.05s ==============================
```

**Confidence Level: ★★★★☆ (4/5)**

The core scheduling behaviors — sorting, filtering, recurrence, conflict detection, and budget-aware planning — are all covered by passing tests, including key edge cases. I held back the fifth star because conflict detection only checks exact time matches (not overlapping durations), and the recurring/conflict features aren't yet exercised end-to-end through the Streamlit UI.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Priority planning | `Scheduler.build_plan()`, `Scheduler.sort_tasks()` | Greedily fits tasks into the time budget, highest priority first (ties broken by shortest duration). |
| Sort by time | `Scheduler.sort_by_time()` | Orders tasks by their `"HH:MM"` time using a `sorted()` lambda key; unscheduled tasks sort last. |
| Filtering | `Scheduler.filter_tasks()` | Filters tasks by pet name and/or completion status (either filter is optional). |
| Recurring tasks | `Task.next_occurrence()`, `Task.is_recurring()`, `Scheduler.mark_task_complete()` | Completing a `daily`/`weekly` task auto-queues a fresh copy with the next `due_date` (via `timedelta`). |
| Conflict detection | `Scheduler.detect_conflicts()` | Lightweight check that returns warning strings when two tasks (same or different pets) share an exact `"HH:MM"` slot — never crashes. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
