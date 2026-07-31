# Possible Pedagogical Extensions

This document collects possible ways to improve interview readiness without
primarily expanding the list of Python subjects. The repository already gives
learners broad technical coverage and repeated practice repairing code against
tests. The largest remaining opportunity is to train and assess the process
around the repair:

> Understand the contract -> form a hypothesis -> gather evidence -> make a
> restrained change -> verify it -> explain the result.

A green test suite measures an important part of that process, but it does not
show how the learner interpreted the problem, chose what to inspect, managed
uncertainty, or communicated trade-offs.

## Extensions That Fit the Current Exercise Model

### Learning mode and interview mode

Use the same underlying exercise in two distinct modes.

**Learning mode** would retain the current README primer, progressive hints,
unlimited working time, and canonical solution. Its purpose is to develop a
correct mental model and a repeatable debugging method.

**Interview mode** would expose only a short candidate brief, the code, and the
tests. It would omit the principle primer, hints, exact bug count, and suggested
investigation sequence. A suggested time box would make planning part of the
task. The learner would still have access to normal Python and shell tools.

Afterward, **debrief mode** would restore the learning material and compare the
attempt against a process rubric. The modes should share one implementation so
that the repository does not acquire two versions of every exercise.

An interview brief should state the business contract, allowed files, and
important constraints. It should not manufacture ambiguity by withholding
information a real interviewer would answer when asked.

### Diagnosis checkpoints

Before editing, ask the learner to record or say:

1. What behavior do the tests specify?
2. Which failure or error should be investigated first, and why?
3. What is the current hypothesis?
4. What is the smallest useful next command or observation?
5. What existing behavior could the proposed repair disturb?

After the suite passes, ask for a short root-cause explanation, a description
of the repair, and one remaining risk or useful additional test. These prompts
make reasoning visible and discourage undirected edit-and-rerun loops.

Research on programming instruction suggests that constructive
self-explanation can improve problem-solving performance, while too much
instructional support can also reduce the learner's constructive work:
[Using Subgoal Learning and Self-Explanation to Improve Programming
Education](https://escholarship.org/uc/item/35z8842x).

### A process rubric

Keep tests as the correctness oracle, but score interview performance
separately. A small rubric could rate each dimension from 0 to 3:

| Dimension | Evidence to look for |
|---|---|
| Contract extraction | Restates observable behavior and relevant constraints |
| Code navigation | Finds relevant code without reading or changing everything |
| Hypothesis quality | Connects evidence to a falsifiable explanation |
| Tool and test selection | Runs focused commands and uses failures diagnostically |
| Repair quality | Makes a restrained, maintainable change that preserves contracts |
| Verification | Runs relevant focused tests and an appropriate regression suite |
| Communication | Explains intent, assumptions, trade-offs, and remaining risks |

The rubric should accept multiple valid repairs. The canonical solution is an
example of sound reasoning, not a patch-shape requirement.

### Cold reattempts and surface variants

Schedule a completed exercise for another attempt after a delay. Record time,
hints used, and rubric scores, then compare them with the first attempt. A
second presentation can rename the domain or reorganize the code while
preserving the underlying failure pattern. This helps distinguish durable
diagnostic skill from memory of a particular patch.

Retrieval practice has produced better delayed retention than additional
restudy in controlled research: [Test-enhanced learning: taking memory tests
improves long-term retention](https://pubmed.ncbi.nlm.nih.gov/16507066/).
The exact benefit of replaying debugging exercises should still be evaluated
within this repository rather than assumed.

### Interviewer follow-up rounds

Once the original suite passes, reveal one additional, explicit requirement.
Examples include preserving backward compatibility, handling a new boundary
value, avoiding a public API change, adding the test that would have prevented
the bug, or explaining behavior under concurrency.

Follow-ups test whether the learner understands the boundary of the repair and
can adapt without discarding working code. A revealed follow-up is generally
more instructive than an unexplained hidden test: it gives the learner an
opportunity to clarify assumptions and discuss the change.

### Faded support

Reduce scaffolding as proficiency grows:

1. Principle primer, detailed hints, and solution.
2. Principle primer and diagnostic prompts, but no repair guidance.
3. Candidate brief and tests only.
4. Candidate brief plus a live follow-up requirement.

The useful measurement is therefore not only whether an exercise was
completed, but also how much support was required.

## Methods That Use Different Artifacts

### Scripted live mock interviews

A peer, instructor, or conversational system follows a standard interviewer
script. The script defines what information is volunteered, how clarification
questions are answered, when a follow-up is introduced, and how the rubric is
applied. Standardization makes separate attempts more comparable while still
practicing live communication.

### Pull-request review simulations

Present a proposed patch rather than a broken working tree. Ask the learner to
identify correctness risks, separate blocking defects from preferences,
suggest missing tests, and write concise review comments. This practices
static code comprehension, prioritization, and professional technical
communication without requiring implementation.

### Ambiguous feature tickets

Begin with working code and an intentionally incomplete change request. The
learner must identify ambiguities, ask clarifying questions, state reasonable
assumptions, add tests, and preserve existing behavior. This complements the
current test-as-specification model by requiring the learner to help establish
the specification.

### Symptom-first incident simulations

Initially provide only a traceback, log excerpt, CI summary, performance
report, or user complaint. Do not identify the relevant module or number of
defects. The learner chooses what to reproduce and inspect, requests additional
evidence, and distinguishes the visible symptom from the root cause. This is a
closer model of brownfield debugging and operational investigation.

The candidate-centered Wheel of Misfortune design and first implementation
plan are developed in [ANALYSIS-TRAINING.md](ANALYSIS-TRAINING.md).

### Recorded think-aloud review

Record a short screen-and-voice attempt, then review it with the process
rubric. The recording can reveal premature editing, overly broad test runs,
unstated assumptions, long directionless periods, and failure to verify beyond
the first green test. Peer review and role-swapping can provide additional
communication practice.

### Short oral retrieval drills

Use five-minute prompts between coding sessions: predict a result, explain a
mock target, identify an invariant, describe a localization strategy, or
compare two repairs. These provide inexpensive, spaced practice in explaining
Python behavior without turning every session into a full exercise.

## Recommended Implementation Order

1. Pilot learning and interview modes on a small set of existing exercises.
2. Add one reusable diagnosis worksheet and one shared process rubric.
3. Track hints used and schedule cold reattempts in addition to recording time.
4. Add standardized interviewer scripts and follow-up prompts for the pilot.
5. Trial one pull-request review and one ambiguous-ticket format.
6. Evaluate whether the modes expose useful differences before expanding them
   across the whole repository.

## Initial Learning/Interview Mode Pilot

The first pilot should represent several interview skills while remaining
small enough to revise the format after observing real attempts.

| Exercise | Why it is a strong candidate | Suggested role |
|---|---|---|
| 05 — Test Interpretation | The tests are the specification and the code is compact, so it cleanly exposes contract-reading and hypothesis formation. | Entry-level calibration |
| 08 — Iteration and Mutation | Three unrelated failure patterns require focused diagnosis without much domain setup. | Core timed debugging |
| 09 — External API Client | Exercises boundary reasoning, mocks, retry semantics, and targeted test reading. | Dependency-boundary interview |
| 12 — Notification Service | Combines dependency injection, time, failure isolation, and maintainability trade-offs. | Advanced single-module interview |
| 20 — Black Box Wrapper | Requires empirical exploration rather than relying only on visible implementation details. | Tool-use and discovery interview |
| 33 — Order Pipeline | Symptoms cross module boundaries and therefore expose navigation, prioritization, and root-cause reasoning. | Longer capstone interview |

Exercises 05 and 08 would be the best place to validate the mechanics of the
mode. Exercises 09, 12, and 20 would then test whether the rubric distinguishes
different kinds of reasoning. Exercise 33 should come last: it is the most
realistic interview simulation, but its size makes it a poor place to debug
the format itself.

A second wave could include exercise 16 for test-double diagnosis, exercise 34
for nondeterministic failures, exercise 35 for debugger fluency, and exercise
40 for a systems-oriented follow-up discussion. These are valuable but more
specialized or operationally awkward under a short, standardized time box.

## Guardrails

- Do not remove or weaken the existing learning material to create interview
  mode; expose a smaller entry point instead.
- Do not use exact bug counts in interview briefs.
- Do not score an exact match to the canonical solution.
- Do not make speed the only success measure. A fast, unexplained repair is not
  equivalent to a clear and verified diagnosis.
- Introduce time pressure after the learner has practiced the underlying
  method. Timers are assessment scaffolding, not instruction.
- Treat hidden tests as regression checks, not substitutes for a stated
  contract or for answering reasonable clarification questions.
