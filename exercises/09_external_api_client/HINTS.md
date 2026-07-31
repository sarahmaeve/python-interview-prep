# Hints: Exercise 09 — External API Client

## Hint 1

Compare request URLs and response keys character-for-character with the tests.

## Hint 2

Check city names containing spaces and count the actual number of network calls
made by the retry loop.

## Hint 3

Use the response key `"temp"`, URL-encode the city query value, and correct the
final-attempt boundary so the advertised number of attempts is available.

The complete walkthrough is in
[solutions/09_solution.md](../../solutions/09_solution.md).
