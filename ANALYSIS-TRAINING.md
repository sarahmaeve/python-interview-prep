# Analysis Training: Tactical Wheel of Misfortune

## Purpose

This document proposes a candidate-centered adaptation of the SRE **Wheel of
Misfortune** for practical Python interview preparation.

The original exercise is interpersonal: a game master presents an incoming
page, selected engineers act as the on-call responders, and the scenario
unfolds as they say what they would investigate or do. Google describes it as
a disaster role-playing exercise resembling a tabletop RPG, often derived
from a previous incident:

- [Accelerating SREs to On-Call and
  Beyond](https://sre.google/sre-book/accelerating-sre-on-call/)
- [Postmortem Culture: Learning from
  Failure](https://sre.google/workbook/postmortem-culture/)

The adaptation here keeps the incoming report, facilitator, staged evidence,
and think-aloud investigation. It narrows the action to a small piece of code.
The report may describe a larger incident, but the learner is asked to analyze
and repair one bounded component within it.

This is **not** incident-command training. It does not assess declaring an
incident, assigning organizational roles, coordinating responders,
communicating with stakeholders, or operating a production system. Those
details may establish urgency and context, but the exercise remains tactical:

> Turn an incomplete report into a sound hypothesis, locate the responsible
> code, make a restrained repair, verify it, and explain the reasoning.

## Why This Complements the Existing Exercises

Most current exercises begin with a reliable test suite and a relatively
complete contract. That is excellent repair practice, but the learner already
knows where the authoritative evidence is and that the implementation contains
the problem.

A tactical Wheel of Misfortune begins earlier:

1. A person, alert, or CI system reports a symptom.
2. The report contains observations, omissions, and possibly an incorrect
   theory about the cause.
3. The learner must decide what the report actually establishes.
4. The learner asks questions and chooses evidence before committing to a
   diagnosis.
5. Tests and source code become evidence within the investigation, rather than
   the complete starting specification.

This adds practice in ambiguity management, evidence selection, hypothesis
revision, and concise technical communication without requiring more Python
subject coverage.

## Learning Objectives

After repeated scenarios, a learner should be able to:

- Restate a vague report as observable behavior without strengthening its
  claims.
- Separate observations, reporter interpretations, correlations, assumptions,
  and unknowns.
- Ask a small number of high-information clarification questions.
- Establish expected behavior, impact, scope, environment, timing, and a
  reproducible case where relevant.
- Form more than one plausible hypothesis and identify evidence that would
  distinguish them.
- Choose focused commands, tests, logs, and code paths instead of inspecting
  everything indiscriminately.
- Revise or discard a hypothesis when evidence contradicts it.
- Distinguish the visible symptom, proximate defect, root cause, and unrelated
  weaknesses noticed along the way.
- Repair the scoped component without attempting to redesign the larger
  system during a time-boxed interview.
- Verify both the reported behavior and relevant regressions.
- Give a short, confident explanation that includes uncertainty where it
  remains.

Google's [Effective
Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/)
describes troubleshooting as an iterative process of observations,
hypotheses, and tests. This plan applies that process to local Python code
rather than production operations.

## Exercise Roles

### Candidate

The candidate receives the initial report and owns the tactical investigation.
They narrate what they know, what they need, which evidence they want, and why.
They may inspect and change only the local exercise workspace.

### Facilitator or game master

The facilitator knows the complete scenario and responds to questions with
prepared facts. They reveal new symptoms or evidence at defined points, ask
the candidate to explain decisions, and avoid steering toward the answer.

The facilitator can be:

- A peer or mentor
- A conversational system following a scenario key
- A self-study reveal sequence stored in the repository

Because this repository is primarily for candidates, every scenario must work
in self-study mode. A live facilitator should improve realism, not be required
to access the material.

### Larger incident context

The scenario may say that an incident commander and other responders are
handling the wider event. The candidate's assignment should then be explicit,
for example:

> The checkout incident is being coordinated elsewhere. You own the
> notification component. Determine whether it can explain the duplicate
> messages, repair any confirmed defect locally, and report your findings.

This preserves the social and operational flavor of the Wheel of Misfortune
without turning a Python repair exercise into an incident-management
simulation.

## Session Format

A normal session should take 35–45 minutes. The stages are deliberately
visible so that the learner practices the whole analysis loop.

### 1. Incoming report — 2 minutes

Read the page, ticket, chat message, CI summary, or customer escalation. Do not
edit code yet.

State:

- The observed symptom as currently reported
- The apparent impact and assigned component
- Any claimed cause that has not yet been demonstrated
- The most important missing information

### 2. Clarification and triage — 3–5 minutes

Ask a short, prioritized set of questions. The objective is not to complete a
bug-report checklist; it is to reduce uncertainty enough to choose the next
action.

If the larger scenario mentions active harm, the candidate may briefly state a
safe mitigation or escalation they would consider. The facilitator then
returns the session to the bounded code task. Production changes are never
performed as part of the repository exercise.

### 3. Evidence gathering — 8–12 minutes

Request or inspect artifacts one at a time. Before each action, state:

- The current hypothesis
- Why this evidence is useful
- What different outcomes would imply

Available evidence may include a traceback, log excerpt, exact command,
environment details, sample input, test result, timing profile, recent diff,
or a focused source-code path.

### 4. Reproduction and localization — 5–10 minutes

Turn the report into the smallest trustworthy local reproduction. Trace the
first point where actual behavior diverges from the contract. A failing
end-to-end test may identify where the defect becomes visible, not where it
originates.

### 5. Repair and verification — 10–15 minutes

Make the smallest maintainable repair justified by the evidence. Run the
focused reproduction first, then an appropriate regression suite. Add or
improve a test when the scenario permits it and the existing test did not
express the reported behavior.

### 6. Handoff — 3 minutes

Summarize:

- What happened
- What evidence established the cause
- What changed
- How the repair was verified
- What remains uncertain or belongs to another component
- One sensible follow-up, if any

A shorter 15-minute mode can stop after diagnosis and proposed verification.
A longer mode can add a follow-up report after the original repair passes.

## Ambiguous Reports

Ambiguity is central to the exercise, but it must be designed rather than
merely vague. A real report often combines partial observations with the
reporter's interpretation. The learner's job is to improve the working model
of the problem, not criticize the reporter.

### Common kinds of ambiguity

| Missing or unclear dimension | Example | Useful candidate response |
|---|---|---|
| Actual behavior | "The export is broken." | Ask what the user or system observed, including exact output or error. |
| Expected behavior | "It returned an empty list." | Establish whether an empty result is invalid for this input. |
| Scope | "Users cannot submit jobs." | Ask which users, requests, tenants, or percentage are affected. |
| Frequency | "It sometimes hangs." | Ask how often, whether it eventually completes, and under what conditions. |
| Timeline | "This started recently." | Establish the first known occurrence and relevant changes around it. |
| Environment | "It works locally." | Compare command, Python version, working directory, configuration, and platform. |
| Input | "Some files fail." | Obtain a minimal failing input and a nearby successful input. |
| Reproduction | "CI is flaky." | Ask for exact commands, run history, test order, seed, and process boundaries. |
| Impact | "This is urgent." | Clarify user-visible harm and the candidate's bounded responsibility. |
| Terminology | "The cache is stale." | Ask what value was observed and why it is believed to be stale. |
| Claimed causality | "The deployment caused it." | Treat timing as correlation until a version comparison or mechanism supports it. |
| Conflated symptoms | "It is slow and duplicates work." | Determine whether the symptoms share requests, timing, or a causal path. |

Useful bug-report templates commonly request current behavior, expected
behavior, reproduction steps, and environment information. See GitHub's
official [issue-form
example](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms?apiVersion=2022-11-28).
The simulation should often omit some of those fields so the candidate must
notice their diagnostic value.

### Observation, inference, and assumption

Scenario material and candidate notes should distinguish these explicitly:

- **Observation:** A named command exited with status 1 and emitted a shown
  traceback.
- **Reported observation:** A customer says they received two confirmations;
  this is evidence, but has not yet been reproduced or correlated.
- **Correlation:** The first report arrived after a deployment.
- **Inference:** The deployment caused the failure.
- **Assumption:** The same request reached the component twice.
- **Unknown:** Whether both confirmations share the same operation identifier.

This vocabulary prevents a confident report from silently becoming a proven
diagnosis.

### Example initial report

> Checkout is timing out for some customers, and support has two reports of
> duplicate confirmation messages. This began after yesterday's retry rollout,
> so the notifier probably is not caching correctly. The main incident is being
> handled by the checkout team. Please fix the notifier.

This is actionable enough to begin but not enough to repair code. It contains:

- A broad incident context: checkout timeouts
- A bounded tactical assignment: the notifier
- Reported observations: two duplicate-message reports
- A correlation: reports followed a retry rollout
- An unproven theory: notifier caching
- Ambiguities: affected versions, frequency, operation identity, exact retry
  path, expected deduplication contract, and whether the duplicate was emitted
  or merely displayed twice

A strong candidate would not ask every possible question. They would first
seek evidence that distinguishes duplicate notifier execution from duplicate
delivery, duplicate display, or two distinct logical operations.

### Fair ambiguity rules

Every scenario should obey these rules:

- The initial report provides enough information to choose at least one useful
  next action.
- Every fact necessary for the tactical diagnosis is discoverable through
  questions, artifacts, tests, or code.
- A reporter may be mistaken, but the scenario must not depend on deliberate
  deception or wordplay.
- At least two hypotheses should be plausible initially.
- No exact wording of a question is required; equivalent investigations earn
  equal credit.
- The broader incident must not conceal an undiscoverable dependency required
  to repair the local component.
- Irrelevant evidence may exist, but it should resemble normal diagnostic
  noise rather than consume most of the time box.
- The initial report should not state the number or location of defects.
- Ambiguity should decrease as good questions are asked.

An authoring target of three to five meaningful omissions, one unproven causal
claim, and at most one distracting detail is enough for most scenarios.

## Evidence and Reveal Mechanics

### Facilitated mode

The game master uses a scenario truth table containing:

- Answers to expected clarification questions
- Equivalent phrasings that should receive the same answer
- Available logs, test results, inputs, and environment facts
- The actual timeline and component boundaries
- Planned injects if the learner stalls or reaches a milestone
- The diagnosis and verification criteria

The game master should answer what was asked, state when information is not
available, and avoid converting every question into a hint.

### Self-study mode

Version one should be document-driven and require no simulation engine. A
scenario can use numbered evidence packets. The learner records the desired
investigation and expected information before opening the corresponding
packet. This is an honor system, like opening `HINTS.md` progressively.

Suggested layout:

```text
analysis_training/
    README.md
    WORKSHEET.template.md
    RUBRIC.md
    scenarios/
        01_example/
            REPORT.md
            CANDIDATE.md
            evidence/
                01.md
                02.md
                03.md
    solutions/
        01_facilitator.md
        01_debrief.md
```

`REPORT.md`, candidate instructions, source comments, and tests must not reveal
the diagnosis. Prepared answers, the scenario truth, and full repair guidance
belong under the canonical `solutions/` area. This follows the repository's
existing spoiler policy.

The source and tests can remain accessible from the beginning. The training
mechanism is the report-first checkpoint and narrated evidence choice, not
artificial file permissions. Some scenarios may delay a specific artifact,
such as a production log excerpt, until it is requested.

### Useful artifacts

- A short alert or CI summary
- A reporter transcript with imprecise language
- Exact success and failure commands
- Tracebacks with irrelevant outer frames
- Structured logs with request or operation identifiers
- A sample input and a neighboring successful input
- Environment or invocation differences
- A recent code or configuration diff
- Repeated-run results for intermittent failures
- A focused profile rather than only a statement that code is slow
- A test that reproduces the report after the learner has defined the contract

Python's [Logging
Cookbook](https://docs.python.org/3/howto/logging-cookbook.html) is a useful
reference when authoring realistic contextual log evidence.

## Assessment Rubric

Score the process independently from the final test result. Each dimension can
use a 0–3 scale: absent, emerging, competent, or strong.

| Dimension | Strong evidence |
|---|---|
| Report interpretation | Separates observed facts, reported claims, assumptions, and unknowns. |
| Clarification | Asks a small number of questions that materially narrow scope or hypotheses. |
| Hypothesis management | Maintains plausible alternatives and updates them when evidence changes. |
| Evidence selection | Chooses focused, low-cost observations and explains what each could distinguish. |
| Localization | Traces the first contract violation rather than repairing only the visible symptom. |
| Repair scope | Changes only what the evidence justifies and preserves neighboring behavior. |
| Verification | Reproduces the report, runs focused checks, and performs appropriate regression testing. |
| Communication | Gives a concise causal account, distinguishes certainty levels, and respects component boundaries. |

Incident-command behavior is deliberately absent from the rubric. Briefly
recognizing that a larger incident may require mitigation or escalation is
reasonable, but it should not dominate the exercise or score.

Do not score the sheer number of questions, commands, or hypotheses. A long
checklist can be less effective than one discriminating question.

## Scenario Authoring Process

1. Choose a known, tested defect or cohesive defect cluster.
2. Define the exact local contract and the repaired behavior.
3. Place that defect inside a plausible larger incident or development event.
4. State the candidate's narrow ownership boundary.
5. Write an initial report containing observations, omissions, and an
   explicitly traceable reporter theory.
6. List at least two initially plausible hypotheses.
7. Build a truth table for likely questions and evidence requests.
8. Prepare artifacts that confirm or disconfirm hypotheses without directly
   naming the faulty line.
9. Define a focused reproduction and regression checks.
10. Write a debrief showing the evidence path, rejected alternatives, repair,
    and other valid investigation routes.
11. Have a reviewer attempt the scenario and flag accidental solution leaks or
    unfair missing facts.

Scenarios should be derived backward from a verified diagnosis. Inventing the
report first and deciding the cause later tends to produce contradictory or
non-diagnostic evidence.

## Candidate Worksheet

A reusable worksheet should remain short enough to use during an interview:

```text
Observed or reported:
Claimed but unproven:
Unknown and important:
Current component boundary:

Hypothesis A:
Hypothesis B:
Next evidence and why:
Result:
Updated belief:

Reproduction:
Root cause:
Repair:
Verification:
Handoff summary:
```

The worksheet is a thinking aid, not paperwork to complete mechanically.

## Pilot Scenarios From Existing Exercises

The first scenarios should reuse cohesive existing failures rather than add
new Python subjects.

The first implemented scenario is [Duplicate Report
Jobs](analysis_training/scenarios/01_duplicate_jobs/REPORT.md), based on
exercise 40. It was selected because an accepted request followed by a lost
response produces a genuine ambiguous production outcome, while the local
repair remains small enough for an interview session.

| Exercise | Larger report | Tactical assignment | Why it fits |
|---|---|---|---|
| 37 — Package Imports | A command works for one developer but fails in CI or under another invocation. | Determine why one package behaves differently across entry points and repair its import behavior. | Naturally ambiguous environment and invocation details reward precise clarification. |
| 40 — Retry Idempotency | Customers report duplicate work after request timeouts during a wider service incident. | Determine whether the local submitter can duplicate or conflate logical operations. | The report can contain plausible but unproven claims about retries, caching, or the server. |
| 34 — Flaky Tests | CI intermittently blocks a release while application behavior appears normal. | Characterize and stabilize the bounded test suite. | Repeated observations and negative evidence matter more than one failure. |
| 33 — Order Pipeline | Operations reports incorrect order or revenue outcomes during a broader commerce incident. | Trace the relevant value across the local pipeline and repair the responsible boundary. | Symptoms can appear far from their causes, making hypothesis-driven navigation visible. |
| 36 — Performance Tuning | A batch job begins missing its processing window as input volume grows. | Reproduce and localize the cost within the supplied Python functions. | Distinguishes measurement from speculation and supports clear performance evidence. |
| 38 — Async Cancellation | A service shutdown or failed batch leaves work running during a larger reliability event. | Diagnose the lifecycle behavior in the local async component. | Provides an advanced scenario where the visible symptom may follow an earlier cancellation mistake. |

Recommended initial sequence:

1. Exercise 40 to validate the format with a genuine ambiguous production
   outcome and competing causal explanations.
2. Exercise 34 to train repeated evidence gathering under nondeterminism.
3. Exercise 33 as the multi-module capstone.
4. Exercise 37 as a later deployment/startup variant centered on invocation
   context rather than an unfolding service incident.

Exercises 36 and 38 can follow after the format is stable because profiling and
async scheduling introduce additional technical load.

## Follow-Up Injects

A Wheel of Misfortune becomes more realistic when the situation changes in
response to progress. For a code-focused session, useful injects include:

- A second reporter describes the symptom differently.
- A nearby successful input narrows the boundary condition.
- A purported recent change is shown to be unrelated.
- The focused repair passes, but a regression test exposes an overbroad change.
- The symptom persists in another component, requiring a clear handoff rather
  than further local edits.
- The candidate learns that an assumed identifier is not stable across retry
  attempts.

Injects must add evidence or a changed requirement. They should not arbitrarily
invalidate sound reasoning or move the goalposts.

## Debrief Design

The debrief should discuss the path, not just show a patch:

- Which phrases in the report were observations and which were theories?
- Which missing fact had the highest information value?
- What were the strongest initial alternative hypotheses?
- Which evidence ruled each alternative out?
- Where did the symptom first become a contract violation?
- Was the repair narrower or broader than necessary?
- What regression check mattered most?
- What should be handed back to the larger incident, and with what certainty?
- What would a strong three-minute interview explanation sound like?

Include more than one valid investigation route when appropriate. The learner
should compare reasoning quality, not reproduce a scripted transcript.

## Implementation Plan

### Phase 1: Paper prototype

- Create the shared candidate worksheet and rubric.
- Author the exercise 40 duplicate-jobs scenario.
- Use Markdown reports, evidence packets, and debriefs only.
- Run the scenario once in self-study mode and once with a facilitator.
- Revise ambiguity that testers find either trivial or unfair.

### Phase 2: Varied evidence

- Add exercise 34 and its repeated-run evidence.
- Add optional follow-up injects to the first scenarios.
- Standardize scenario truth tables and facilitator guidance.
- Record completion time, hints or evidence packets opened, and rubric scores.

### Phase 3: Capstone

- Adapt exercise 33 as a longer multi-module scenario.
- Add a diagnosis-only time-boxed variant.
- Compare performance with the same learner's ordinary README-first attempt.
- Decide whether the approach merits expansion to exercises 36 and 38.

No simulation engine is needed until the document-driven format has been
tested. If automation is later useful, it should reveal prepared artifacts and
record choices; it should not attempt to judge arbitrary natural-language
questions as correct or incorrect.

## Acceptance Criteria

The pilot is successful when:

- A learner can complete every scenario without a human facilitator.
- A live facilitator can run the same scenario consistently from its truth
  table.
- The initial report is incomplete but provides a productive first move.
- All decisive facts are discoverable.
- At least two reasonable investigation paths can reach the diagnosis.
- No candidate-facing file or source comment reveals the repair.
- The local repair is verified by tests.
- The rubric distinguishes a lucky patch from a well-supported diagnosis.
- The larger incident provides context without expanding the task into
  incident command.
- Debrief feedback improves the learner's next investigation, rather than only
  confirming whether the patch matched the solution.
