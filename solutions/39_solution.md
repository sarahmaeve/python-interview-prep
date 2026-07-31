# Solution: Exercise 39 — Equality and Hashing Contracts

## Bugs Found

1. `ProductCode.__eq__` compares case-folded values, but `__hash__` hashes the
   original spelling. Equal codes can occupy different set or dictionary
   buckets.
2. `Version.__eq__` assumes every other object has `.parts`, so an unsupported
   comparison raises `AttributeError` and prevents reflected comparison.
3. `AccountKey` forces a generated hash while its identity fields remain
   mutable. Mutation after insertion can make a key unreachable.

## Repairs

Hash the same canonical representation used by equality:

```python
def __hash__(self) -> int:
    return hash(self.value.casefold())
```

Two unequal values may share a hash, but two equal values must share one.

Cooperate with foreign operand types:

```python
def __eq__(self, other: object) -> bool:
    if not isinstance(other, Version):
        return NotImplemented
    return self.parts == other.parts
```

Returning `NotImplemented` lets Python try the reflected comparison. It is not
the same as returning `False`, raising `NotImplementedError`, or returning the
`NotImplemented` class.

Make the logical key immutable:

```python
@dataclass(frozen=True)
class AccountKey:
    tenant_id: str
    user_id: str
```

With `eq=True` and `frozen=True`, dataclasses generate a compatible hash and
raise `FrozenInstanceError` on ordinary field assignment. This is shallow
immutability: a frozen dataclass can still refer to a mutable object, so fields
participating in the hash must themselves have stable hashes.

## Design Notes

- Defining `__eq__` without `__hash__` normally makes a class unhashable. That
  is a safety feature for mutable value objects.
- Equality normalization and hash normalization must evolve together. Extract
  a private canonical-value helper when the rule is nontrivial.
- `NotImplemented` enables cooperation between numeric types and other
  compatible representations. Unsupported ordering comparisons normally end
  in `TypeError`; unsupported equality normally falls back to unequal.

## Official documentation

- [Value comparison](https://docs.python.org/3/reference/datamodel.html#object.__eq__)
- [Hashing](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Dataclass hashing and freezing](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass)
