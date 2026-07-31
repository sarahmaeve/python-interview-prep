# Exercise 39: Equality and Hashing Contracts

Three small value-object classes are used in comparisons, sets, and dictionary
keys. They appear to work for ordinary examples, but violate three parts of
Python's data-model contract.

**This exercise practices:** cooperative equality, the relationship between
equality and hashing, and why hashable keys need stable identity-relevant
state.

## How to run the tests

```bash
cd exercises/39_equality_and_hashing
python3 -m unittest test_value_objects -v
```

Edit `value_objects.py`; do not modify the tests. There are **3 bugs**.

## Equality is a relation

A useful value equality should be reflexive, symmetric, and transitive. Python
implements comparisons cooperatively: `left == right` first gives the left
operand an opportunity, and if that implementation returns `NotImplemented`,
Python can try the reflected operation on the right operand.

`NotImplemented` is a singleton return value, not the
`NotImplementedError` exception. It means “I do not know how to compare with
this type.” Returning it is usually better than assuming foreign attributes
exist, and can be more correct than immediately returning `False` when another
type deliberately supports the comparison.

## The hash invariant

Sets and dictionaries use a hash to choose where to look, then equality to
resolve candidates. Python requires:

```text
if a == b, then hash(a) == hash(b)
```

The reverse is not required: unequal objects may collide. If equality uses a
normalized representation—case-folded text, rounded coordinates, canonical
paths—the hash must use that same representation.

## Hashes must remain stable

After an object becomes a dictionary key or set member, changing a field that
affects its hash can leave it stored in the old bucket but searched for in a
new one. That makes the object appear to vanish from the collection.

Python therefore makes ordinary mutable dataclasses unhashable by default.
`unsafe_hash=True` overrides that protection and should be used only when the
fields participating in equality are logically immutable. For value keys,
`frozen=True` often expresses the intended contract more honestly.

For another runnable value-object example, see
[Guide 02](../../guides/02_classes_and_oop.py), section 4b.

If you get stuck, use [HINTS.md](HINTS.md).

## Official Python documentation

- [Value comparison and `__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__eq__)
- [`__hash__` requirements](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [`NotImplemented`](https://docs.python.org/3/library/constants.html#NotImplemented)
- [`@dataclass`, `frozen`, and `unsafe_hash`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass)
