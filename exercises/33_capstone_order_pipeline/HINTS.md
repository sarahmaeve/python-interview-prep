# Hints: Exercise 33 — Order Pipeline

## Hint 1

There is roughly one bug per module. Some failing assertions are downstream
symptoms.

## Hint 2

Revisit mutable defaults, normalized lookup keys, swallowed pricing errors,
status sentinels, and accumulation for repeated customers.

## Hint 3

Use per-order line storage, normalize lookup consistently, reject an unknown
SKU explicitly, use the status constant exactly, and accumulate rather than
replace a customer's revenue.

The module-by-module repair is in
[solutions/33_solution.md](../../solutions/33_solution.md).
