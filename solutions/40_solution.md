# Solution: Exercise 40 — Retry Idempotency

## Bugs Found

1. The submitter generates a new idempotency key inside the retry loop. An
   ambiguous first attempt and its retry therefore create separate remote jobs.
2. Completed results are detected by truthiness, so valid results such as `0`
   are submitted again.
3. The payload record is overwritten before checking existing state. Reusing a
   key for a different request silently returns or replaces unrelated work.

## Repairs

Register the logical operation without overwriting an existing request:

```python
operation_id = operation_id or self._key_factory()
if operation_id in self._payloads:
    if self._payloads[operation_id] != payload:
        raise IdempotencyConflict(
            f"operation {operation_id!r} was already used for another payload"
        )
else:
    self._payloads[operation_id] = payload
```

Use membership for the completion cache:

```python
if operation_id in self._results:
    return self._results[operation_id]
```

Finally, pass the logical operation ID to every attempt:

```python
for _ in range(max_attempts):
    try:
        result = self.gateway.submit(
            payload,
            idempotency_key=operation_id,
        )
    except TransientSubmissionError as exc:
        last_error = exc
    else:
        self._results[operation_id] = result
        return result
```

The gateway can now recognize a replay after an accepted request whose response
was lost. The second attempt retrieves job `100` instead of creating job `101`.

## Production Considerations

This repaired implementation explains the protocol but is not concurrency-safe
or durable. A production design normally needs:

- one atomic insert-or-read operation protected by a database uniqueness
  constraint or transaction;
- an explicit state machine such as `in_progress`, `completed`, and `failed`;
- a canonical payload digest and a defined key namespace;
- retention and expiration rules;
- recovery for a worker that crashes while an operation is `in_progress`;
- authorization preventing one caller from probing another caller's keys.

Idempotency does not make every failure retryable. Retry classification,
backoff, and idempotency solve different problems: whether to try again, when
to try again, and how to avoid duplicating effects if an attempt is replayed.

## References

- Python [`uuid.uuid4`](https://docs.python.org/3/library/uuid.html#uuid.uuid4)
- Python [dictionary operations](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- [HTTP idempotent methods, RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)
