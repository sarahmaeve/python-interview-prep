# Study Guide: Making the Most of Your Prep Time

This document helps you prioritize based on how much time you have before the interview.

## If You Have 2 Hours

Skip the guides. Go straight to exercises and learn by doing.

1. **Exercise 05 — User Validator** (30 min) — Practice reading tests as a specification and fixing validation bugs. This directly mirrors the interview format.
2. **Exercise 08 — Task Manager** (30 min) — Three subtle bugs (iteration mutation, date comparison, generator exhaustion) that require careful reasoning.
3. **Exercise 12 — Notification Service** (30 min) — Capstone exercise covering dependency injection, mocking, and testability.
4. **Exercise 18 — String Calculator** (30 min) — Write tests from scratch for working code. Practices the "improving tests" skill.

After each exercise, read the solution file in `solutions/` to check your diagnosis process.

## If You Have 4 Hours

Add the guides that cover your weakest areas, plus more exercises.

**Hour 1: Targeted reading**
- Skim `guides/03_unittest_fundamentals.py` if you're rusty on unittest
- Skim `guides/05_mocking_and_external_deps.py` if you haven't used mocks

**Hours 2-4: Exercises**
1. Exercise 03 — Bank Account (class attribute vs instance attribute)
2. Exercise 05 — User Validator (reading tests as spec)
3. Exercise 08 — Task Manager (iteration, generators, dates)
4. Exercise 09 — Weather Client (mocking external APIs)
5. Exercise 12 — Notification Service (capstone)
6. Exercise 18 or 19 — Write tests from scratch

## If You Have a Full Day (6-8 Hours)

**Morning: Guides** (2-3 hours)
Read and run guides 01-05 in order. These build on each other:
- Guide 01 → needed for exercises 01-08
- Guide 02 → needed for exercises 03, 04, 17
- Guide 03 → needed for all exercises (you're reading tests constantly)
- Guide 04 → directly applicable to every debugging exercise
- Guide 05 → needed for exercises 09-12, 15-16, 19

**Afternoon: Exercises** (3-4 hours)
Work through this sequence, which hits every major skill:
1. Exercise 01 — Shopping Cart (warm up)
2. Exercise 05 — User Validator (test interpretation)
3. Exercise 06 — Event Logger (mutable defaults, defensive copying)
4. Exercise 08 — Task Manager (iteration, generators)
5. Exercise 09 — Weather Client (mocking)
6. Exercise 12 — Notification Service (capstone)
7. Exercise 18 — String Calculator (write tests)
8. Exercise 16 — Inventory Service (fix broken mocks)

**Evening: Review** (1 hour)
- Read guides 06-07 (clean code, type hints)
- Attempt exercise 19 (write tests with mocks) if time allows

## If You Have Multiple Days

Work through everything in order. The exercises are numbered by difficulty within each section:
- **01-04**: Beginner (functions, strings, classes, inheritance)
- **05-08**: Intermediate (test reading, mutable state, exceptions, iteration)
- **09-12**: Advanced (mocking, time, file I/O, testability)
- **13-14**: Type hinting (bugs and annotations)
- **15-16**: Mock mastery (write mocks, fix broken mocks)
- **17**: OOP patterns (properties, composition)
- **18-19**: Test writing (basic and with mocks)
- **20-22**: Black box interaction, observability, systems integration

## Key Skills by Interview Area

| Interview Focus | Most Relevant Exercises |
|----------------|------------------------|
| Debugging unfamiliar code | 01, 02, 05, 08, 13 |
| Test-driven workflow | 05, 14, 18, 19 |
| External interactions / mocking | 09, 10, 11, 15, 19 |
| Clean, maintainable code | 06, 07, 12, 17 |
| Improving tests | 16, 18, 19 |
| Black box / opaque dependencies | 20 |
| Observability / logging | 21 |
| Systems dialogue (CI/CD, env, retries) | 22 |

## Guide-to-Exercise Prerequisites

| Exercise | Read First |
|----------|-----------|
| 01-04 | Guide 01 (functions), Guide 02 (classes) |
| 05-08 | Guide 03 (unittest), Guide 04 (debugging) |
| 09-12 | Guide 05 (mocking) |
| 13-14 | Guide 07 (type hints) |
| 15-16 | Guide 05 (mocking) |
| 17 | Guide 02 (classes — properties, composition) |
| 18 | Guide 03 (unittest) |
| 19 | Guide 03 (unittest), Guide 05 (mocking) |
| 20 | Guide 05 (mocking — adapter concepts) |
| 21 | Guide 08 (observability) |
| 22 | Guide 08 (observability — env config, CI/CD sections) |
