# Analysis Training

This directory contains symptom-first debugging scenarios based on the SRE
**Wheel of Misfortune**. Each scenario begins with an incomplete report rather
than an exercise specification. The learner clarifies the report, requests
evidence, forms and revises hypotheses, repairs a bounded Python component,
and gives a short handoff.

The broader design is in
[ANALYSIS-TRAINING.md](../ANALYSIS-TRAINING.md).

## How to use a scenario

1. Open only the scenario's `REPORT.md` and `CANDIDATE.md`.
2. Record an initial analysis before inspecting code or opening evidence.
3. Use `REQUESTS.md` to reveal only evidence you would have requested.
4. Narrate what each investigation is expected to distinguish.
5. Reproduce, repair, and verify the bounded component.
6. Open follow-up injects only when the candidate instructions say to.
7. Score the attempt with [RUBRIC.md](RUBRIC.md).
8. Read the canonical debrief under `solutions/analysis_training/`.

The files are not access-controlled. Self-study mode uses the same honor system
as the exercise hints and solutions: revealing less information produces a
more realistic attempt.

## Available scenarios

| # | Scenario | Source component | Suggested time |
|---|---|---|---|
| 01 | [Duplicate jobs after a gateway incident](scenarios/01_duplicate_jobs/REPORT.md) | Exercise 40 job submitter | 35–45 minutes |

## Live facilitation

A peer can act as game master instead of using the evidence menu. The
facilitator guide is deliberately kept with the canonical solutions so that it
does not appear in the candidate path.

