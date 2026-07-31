# Debrief: Duplicate Report Jobs

Read this only after completing the scenario and follow-up injects.

## What the initial report established

The report established that customers saw duplicate jobs around apparent
timeouts and that the Python submitter was the assigned component. It did not
establish that the gateway, retry policy, key generation, cache, or recent
deployment caused the behavior.

The most valuable missing relationship was the identity mapping:

> Did one caller operation produce both jobs, and which idempotency key did the
> gateway receive for each attempt?

The correlated trace answered both parts. One `operation-7` invocation sent
`attempt-a` and `attempt-b`; the gateway therefore treated them as different
operations. Its repeated-key contract showed that the client could safely
replay the first key instead.

## Primary diagnosis

`JobSubmitter.submit` establishes or accepts an operation ID before entering
the retry loop, but the broken implementation generates another key inside the
loop and sends that attempt key to the gateway.

The transport error is ambiguous: the first job can commit even though its
response is lost. A second attempt with a fresh key creates another job. The
operation ID—not the attempt number—must name every attempt belonging to that
logical submission.

After repair, the local reproduction still makes two gateway calls because the
first response is lost, but both calls carry `operation-7`. The gateway records
one job and returns that same result on replay.

## Follow-Up 1

The component stores result `0`, but `_results.get(operation_id)` returns `0`,
which is falsy. Truth-value testing cannot distinguish a missing key from a
present key whose valid value is falsy.

The contract is about cache membership, so the repair checks whether the
operation ID is present before returning its stored result.

## Follow-Up 2

The broken implementation writes the new payload to `_payloads` before asking
whether the operation already exists. That destroys the evidence needed to
detect conflicting reuse. A truthy cached result may then be returned for an
unrelated request.

The repair first checks the recorded payload. An identical payload is a replay;
a different payload raises `IdempotencyConflict`; a new operation records its
payload.

See [the complete exercise solution](../40_solution.md) for repair snippets and
production considerations.

## Other sound investigation paths

- Begin with the deterministic reproduction and compare `gateway.calls` with
  `gateway.accepted`.
- Read the gateway test double to infer its repeated-key contract, then trace
  every invocation of the key factory.
- Start from the caller operation ID and follow its representation across the
  local/remote boundary.

Each path is sound if the candidate states what the evidence demonstrates and
does not assume that a timeout proves remote failure.

## Reflection

- Which phrase in the initial report tempted you toward an unsupported cause?
- Which question reduced the most uncertainty?
- Did you predict what each command could distinguish before running it?
- Did the follow-up injects change your model of operation identity or only
  reveal additional lines to patch?
- Could you explain the trigger, defect, symptom, and repair separately in
  three minutes?

