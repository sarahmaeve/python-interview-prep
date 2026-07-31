# Candidate Instructions

Suggested time: **35–45 minutes**.

Your working component is
`exercises/40_retry_idempotency/job_submitter.py`. You may modify that file.
Do not modify its existing tests or the incident reproduction.

For this attempt, do not read the exercise README, hints, or canonical
solutions. They are learning-mode material and identify the underlying topic
too directly.

## Stage 1: Analyze the report

Before opening source code or running tests, record:

- What the report establishes
- What it merely suggests
- The component boundary you own
- At least two plausible explanations
- Your first three clarification questions, in priority order

Use [the shared worksheet](../../WORKSHEET.template.md) as a prompt, or take
equivalent notes elsewhere.

## Stage 2: Request evidence

After writing your own questions, open [REQUESTS.md](REQUESTS.md). It maps
common investigation requests to evidence packets. Open only the packets that
correspond to actions you would actually take.

Before each packet, state what you expect it to distinguish. Afterward, update
or reject a hypothesis.

You may inspect the assigned source whenever your investigation justifies it.
Do not begin by running the complete unit-test suite: preserving the staged
symptoms is part of this simulation, not general advice about debugging.

## Stage 3: Reproduce and repair the reported symptom

Use the local incident reproduction when you decide that it is useful. Repair
only behavior supported by the report and gathered evidence.

Verify the primary symptom with both the reproduction and this focused test:

```bash
cd exercises/40_retry_idempotency
python3 -m unittest \
  test_job_submitter.TestStableOperationIdentity.test_ambiguous_retry_creates_only_one_remote_job \
  -v
```

Do not open an inject until that focused test passes.

## Stage 4: Respond to follow-up injects

Open and resolve these in order:

1. [Inject 1](injects/01.md)
2. [Inject 2](injects/02.md)

Treat each inject as new evidence. State the contract before editing, then run
the focused verification it supplies.

## Stage 5: Verify and hand off

Run the entire exercise suite:

```bash
cd exercises/40_retry_idempotency
python3 -m unittest test_job_submitter -v
```

Give a three-minute handoff covering:

- The original symptom and root cause
- The evidence that distinguished it from other explanations
- The repair and regression verification
- How each follow-up extended the contract
- Production concerns that the local in-memory component cannot settle

Score the attempt with [the shared rubric](../../RUBRIC.md), then read the
[canonical debrief](../../../solutions/analysis_training/01_duplicate_jobs_debrief.md).
