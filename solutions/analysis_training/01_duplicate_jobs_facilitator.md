# Facilitator Guide: Duplicate Report Jobs

This guide contains the scenario truth and must not be shown to the candidate
before the session.

## Purpose

The primary incident tests whether the candidate distinguishes one logical
operation from its transport attempts. The follow-up injects test completed
result presence and conflicting reuse of operation identity.

The scenario is tactical. The facilitator should acknowledge sensible comments
about mitigation or incident coordination, then return ownership to the local
`JobSubmitter` component.

## Opening

Give the candidate only:

- `analysis_training/scenarios/01_duplicate_jobs/REPORT.md`
- `analysis_training/scenarios/01_duplicate_jobs/CANDIDATE.md`
- The assigned source when they choose to inspect it

Do not volunteer the gateway trace, repeated-key contract, or number of
component defects.

## Scenario truth

- One caller invocation represents one logical operation.
- The first gateway request commits job `100`, but its response is lost.
- The retry uses a new key and commits job `101`.
- The gateway correctly deduplicates only repeated uses of the same key.
- The recent incident made an old client defect visible more frequently.
- The primary incident is fully reproducible locally.

## Question and evidence guide

| Candidate investigation | Response |
|---|---|
| Asks how many callers or logical submissions were involved | Reveal Packet 1. |
| Asks whether the first attempt committed before the error | Reveal Packet 2. |
| Asks to correlate operation IDs, attempt IDs, keys, or jobs | Reveal Packet 3. |
| Asks how the gateway treats retries or repeated keys | Reveal Packet 4. |
| Asks what changed or whether this is environment-specific | Reveal Packet 5. |
| Requests a safe reproduction | Reveal Packet 6. |
| Asks for production access or to mutate live state | State that the incident team owns production; offer the local reproduction. |
| Asks for unavailable user-specific data | State that it is unavailable and ask whether it blocks local diagnosis. |

Equivalent questions should receive the same evidence. Do not require the
candidate to use terms such as “logical operation” or “idempotency” before the
evidence supports them.

## Expected primary reasoning

A strong investigation usually notices that two jobs can be legitimate if two
independent logical requests occurred. It therefore asks for correlation among
the caller operation, gateway keys, and accepted jobs.

Packet 3 shows that one caller operation produced two new keys. Packet 4 then
establishes that the gateway interprets those keys as separate operations. In
the source, the key factory is called inside the retry loop even though a
caller operation ID already exists.

The repair passes the stable operation ID to every gateway attempt. The local
reproduction should change from two accepted jobs (`100` and `101`) to one
accepted job (`100`) returned on replay.

## Inject timing

Reveal Inject 1 only after the ambiguous-retry test passes. Reveal Inject 2
only after the falsy-result test passes.

If the candidate ran the full suite early and already saw the additional
failures, keep the narrative order but do not penalize normal test use. Ask
them to separate the original incident from independently discovered contract
failures.

## Common premature conclusions

- **“The gateway is broken.”** Ask what the gateway received and whether it
  violated its stated repeated-key contract.
- **“Retries are unsafe and should be removed.”** Ask whether a response can be
  lost before or after acceptance, and whether stable identity can make replay
  safe.
- **“The deployment caused the code bug.”** Provide change history and ask the
  candidate to distinguish trigger from defect.
- **“Zero means failure.”** The Inject 1 contract explicitly defines zero as a
  successful result.
- **“Returning the old result is always idempotent.”** Ask whether the old and
  new requests represent the same intent.

## Verification

The candidate should run:

1. `python3 reproduce_incident.py`
2. The focused stable-operation test
3. Each inject's focused test
4. `python3 -m unittest test_job_submitter -v`

The repaired implementation should pass all six exercise tests. The exact
repair and production limitations are documented in
[the exercise solution](../40_solution.md).

## Model handoff

The gateway incident exposed a pre-existing client identity bug. One logical
submission kept caller operation ID `operation-7`, but each retry sent a new
gateway key, so a lost response followed by retry created two jobs. The client
now passes the logical operation ID on every attempt, and the reproduction
creates one remote job that is returned on replay.

Follow-up verification found two related local contract defects: cached result
`0` was mistaken for absence, and reuse of an operation ID could overwrite its
recorded payload instead of rejecting a conflict. Those checks now use key
presence and preserve the original payload identity. The incident
reproduction, focused cases, and full six-test suite pass. Durable,
concurrency-safe cross-process storage remains outside this in-memory
component.

