"""Inventory audit pipeline — 3 bugs that are easier to STEP to than to see.

A small pipeline: parse raw CSV lines, merge duplicate SKUs, apply
manual adjustments, and total everything up.  Each function looks
plausible; the bugs only show themselves in how data CHANGES as it
flows through.

Your job:
  - Find and fix 3 bugs — using the debugger, not print statements.
    (See README.md for a pdb crash course and a suggested session.)
  - All tests must pass without modification.

Relevant reading: exercises/35_debugging_with_pdb/README.md,
guides/04_debugging_strategies.py.
"""


def parse_rows(raw_lines):
    """Parse "sku,qty" CSV lines into row dicts.

    The FIRST line is a header and is skipped; every other line is data.
    """
    rows = []
    for line in raw_lines[1:-1]:
        sku, qty = line.strip().split(",")
        rows.append({"sku": sku.strip(), "qty": int(qty)})
    return rows


def merge_duplicates(rows):
    """Combine rows that share a SKU by summing their quantities.

    Returns a NEW list of NEW row dicts — *rows* and the dicts inside it
    must not be modified.  (Callers keep using their originals.)
    """
    merged = {}
    for row in rows:
        sku = row["sku"]
        if sku in merged:
            merged[sku]["qty"] += row["qty"]
        else:
            merged[sku] = row
    return list(merged.values())


def apply_adjustments(rows, adjustments):
    """Apply each {"sku", "delta"} adjustment to the row with that SKU.

    Adjustments whose SKU matches no row are ignored.  Returns *rows*.
    """
    for adjustment in adjustments:
        target_sku = adjustment["sku"]
        delta = adjustment["delta"]
        for row in rows:
            if row["sku"] == target_sku:
                new_qty = row["qty"] + delta
        row["qty"] = new_qty
    return rows


def total_units(rows):
    """Total units across all rows."""
    return sum(row["qty"] for row in rows)


def audit_report(raw_lines, adjustments=()):
    """End-to-end: parse, merge duplicates, adjust, and summarise.

    Returns {"rows": [...], "total": int}.
    """
    rows = parse_rows(raw_lines)
    merged = merge_duplicates(rows)
    adjusted = apply_adjustments(merged, list(adjustments))
    return {"rows": adjusted, "total": total_units(adjusted)}
