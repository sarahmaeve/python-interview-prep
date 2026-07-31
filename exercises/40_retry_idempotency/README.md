# Exercise 40: Retry Idempotency

A job submitter retries transient transport failures and remembers completed
operations. The retry loop works when failures happen before the remote side
acts, but ambiguous outcomes and key reuse expose three idempotency bugs.

**This exercise practices:** distinguishing an attempt from a logical
operation, handling falsy cached results correctly, and detecting conflicting
reuse of an idempotency key.

## How to run the tests

```bash
cd exercises/40_retry_idempotency
python3 -m unittest test_job_submitter -v
```

Edit `job_submitter.py`; do not modify the tests. There are **3 bugs**.

## Why retries can duplicate work

A transport error does not prove the remote operation failed. The server might
have committed a job and the response might have been lost afterward. Retrying
that logical operation as a fresh request can create a second job.

This creates two different identities:

- An **attempt** is one network call and can occur several times.
- A **logical operation** is the caller's single intent and must retain one
  identity across all attempts.

An idempotency key names the logical operation. A cooperating receiver records
the outcome for that key and returns the same outcome when an attempt is
replayed. Generating a new key for each retry defeats that protocol.

## Key reuse and request identity

The same key and the same request mean “resume or replay this operation.” The
same key with a different request is a conflict, not a cache hit. Production
systems commonly store a canonical request fingerprint beside the result and
reject mismatches.

Key scope and retention are domain decisions. A key may be unique per customer
for 24 hours, per account indefinitely, or within another explicit namespace.
Random UUIDs are useful defaults, but callers need a way to persist and resend
the chosen key after a timeout.

## Presence is not truthiness

A completed operation can validly return `0`, `False`, an empty collection, or
another falsy value. Cache membership must therefore be checked by key
presence, not by the truth value of the stored result.

## Limits of the exercise

The in-memory dictionaries demonstrate the protocol but are not a production
idempotency store. Concurrent workers need an atomic uniqueness constraint or
transaction, and multiple processes need shared durable storage. Retention,
recovery after crashes, payload canonicalization, and authorization of key
reuse also need explicit designs.

If you get stuck, use [HINTS.md](HINTS.md).

## Official references

- Python [`uuid.uuid4`](https://docs.python.org/3/library/uuid.html#uuid.uuid4)
- Python [mapping types — `dict`](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- Python [truth-value testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
- [HTTP idempotent methods, RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)

HTTP method idempotency and application-level idempotency keys are related but
not identical: this exercise implements the latter for an operation that may
otherwise create a new remote resource.
