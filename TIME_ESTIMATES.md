# Exercise Time Estimates

Estimated completion times for a prepared developer who has read the relevant guides.
Use this to compare against your actual times when testing the material.

## Debug Exercises (fix buggy code, tests are correct)

| # | Exercise | Bugs | Format | Est. Time | Difficulty Drivers |
|---|----------|------|--------|-----------|-------------------|
| 01 | Shopping Cart | 3 | Fix impl | 10 min | Short code, isolated bugs (type coercion, formula, format inconsistency) |
| 02 | Text Formatter | 3 | Fix impl | 15 min | String manipulation edge cases; truncate length math |
| 03 | Bank Account | 3 | Fix impl | 15 min | Class vs instance attribute; cascading bugs (withdraw return → transfer) |
| 04 | Shapes | 3 | Fix impl | 15 min | Inheritance chain; missing `()` on method call; wrong formula |
| 05 | User Validator | 4 | Fix impl | 20 min | Must read tests as spec; 4 independent validation bugs; bare except |
| 06 | Event Logger | 3 | Fix impl | 20 min | Mutable default arg; defensive copying; in-place mutation side effect |
| 07 | Config Parser | 3 | Fix impl | 20 min | Exception handling subtleties; bare except; lost context in re-raise |
| 08 | Task Manager | 3 | Fix impl | 20 min | List mutation during iteration; generator exhaustion; date string trap |
| 09 | Weather Client | 3 | Fix impl | 25 min | Mock-based tests add reading time; URL encoding; retry off-by-one |
| 10 | Cache with Expiry | 3 | Fix impl | 25 min | Mocked time; boundary condition (>= vs >); dict mutation during iteration |
| 11 | CSV Report | 3 | Fix impl | 25 min | mock_open pattern; file handle leak; accumulator overwrite; error propagation |
| 12 | Notification Service | 4 | Fix impl | 30 min | Dependency injection; 4 bugs across DI, clock, template, loop control |
| 13 | Grade Processor | 4 | Fix impl | 15 min | Type mismatch bugs; None returns; list-vs-dict confusion |
| 17 | Temperature Monitor | 4 | Fix impl | 15 min | @property missing; @setter missing; composition reference bug; None filtering |

## Type Hinting Exercises

| # | Exercise | Format | Est. Time | Difficulty Drivers |
|---|----------|--------|-----------|-------------------|
| 14 | Task Registry | Add hints | 10 min | 11 method signatures; docstrings guide the work; Optional/list/dict types |

## Mock Exercises

| # | Exercise | Format | Est. Time | Difficulty Drivers |
|---|----------|--------|-----------|-------------------|
| 15 | Payment Processor | Write mocks | 15 min | 10 TODO stubs; mix of spec, return_value, side_effect, patch, chaining |
| 16 | Inventory Service | Fix broken mocks | 15 min | 4 mock bugs: wrong patch target, typo, wrong return type, decorator order |

## Write Tests Exercises

| # | Exercise | Format | Est. Time | Difficulty Drivers |
|---|----------|--------|-----------|-------------------|
| 18 | String Calculator | Write tests | 10 min | 10 stub tests; clear spec; straightforward assertions |
| 19 | Order Service | Write tests + mocks | 20 min | 10 stub tests; must mock 2 injected clients + patch urlopen |

## Black Box / Observability / Systems

| # | Exercise | Bugs | Format | Est. Time | Difficulty Drivers |
|---|----------|------|--------|-----------|-------------------|
| 20 | Black Box Wrapper | 3 | Fix wrapper | 20 min | Must discover black box quirks via introspection; adapter pattern; mutable default |
| 21 | Observability & Logging | 3 | Fix impl | 25 min | logging module; assertLogs in tests; silent error swallowing; log levels |
| 22 | Systems Integration | 3 | Fix impl | 25 min | Environment config; import-time evaluation; timeout passing; CI flag injection |

## Summary by Time

| Time | Exercises |
|------|-----------|
| 10 min | 01, 14, 18 |
| 15 min | 02, 03, 04, 13, 15, 16, 17 |
| 20 min | 05, 06, 07, 08, 19, 20 |
| 25 min | 09, 10, 11, 21, 22 |
| 30 min | 12 |

## Notes

- Times assume the developer has read the relevant guide(s) and is familiar with the concepts.
- "Reading the tests" is a significant portion of time for exercises 09-12 due to mock setup complexity.
- Exercise 20 requires exploring an opaque module first — budget extra time for introspection.
- Exercise 22 includes discussion questions with no single right answer — practice articulating trade-offs aloud.
- Your actual times will likely be faster than these estimates on exercises where you're strong, and slower on exercises that cover your weak spots — that's the point. Use the gaps to identify what to study more.

## Your Times

| # | Exercise | Estimated | Your Time | Delta | Notes |
|---|----------|-----------|-----------|-------|-------|
| 01 | Shopping Cart | 10 min | | | |
| 02 | Text Formatter | 15 min | | | |
| 03 | Bank Account | 15 min | | | |
| 04 | Shapes | 15 min | | | |
| 05 | User Validator | 20 min | | | |
| 06 | Event Logger | 20 min | | | |
| 07 | Config Parser | 20 min | | | |
| 08 | Task Manager | 20 min | | | |
| 09 | Weather Client | 25 min | | | |
| 10 | Cache with Expiry | 25 min | | | |
| 11 | CSV Report | 25 min | | | |
| 12 | Notification Service | 30 min | | | |
| 13 | Grade Processor | 15 min | | | |
| 14 | Task Registry | 10 min | | | |
| 15 | Payment Processor | 15 min | | | |
| 16 | Inventory Service | 15 min | | | |
| 17 | Temperature Monitor | 15 min | | | |
| 18 | String Calculator | 10 min | | | |
| 19 | Order Service | 20 min | | | |
| 20 | Black Box Wrapper | 20 min | | | |
| 21 | Observability & Logging | 25 min | | | |
| 22 | Systems Integration | 25 min | | | |
| | **Total** | **370 min (~6 hrs)** | | | |
