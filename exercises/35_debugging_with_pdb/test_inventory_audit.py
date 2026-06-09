"""Tests for the inventory audit pipeline.

Do NOT modify this file.  Fix the bugs in inventory_audit.py until every
test passes.  This exercise is about HOW you find them — see README.md
for the pdb workflow.
"""

import unittest

from inventory_audit import (
    apply_adjustments,
    audit_report,
    merge_duplicates,
    parse_rows,
    total_units,
)

RAW = [
    "sku,qty",        # header
    "COF-1,10",
    "TEA-2,4",
    "MUG-3,7",
]


class TestParseRows(unittest.TestCase):

    def test_header_is_skipped(self):
        rows = parse_rows(RAW)
        self.assertNotIn("sku", [row["sku"] for row in rows])

    def test_every_data_line_is_parsed(self):
        rows = parse_rows(RAW)
        self.assertEqual(
            [row["sku"] for row in rows],
            ["COF-1", "TEA-2", "MUG-3"],
            "all three data lines must produce a row",
        )

    def test_quantities_are_ints(self):
        rows = parse_rows(RAW)
        self.assertEqual(rows[0], {"sku": "COF-1", "qty": 10})


class TestMergeDuplicates(unittest.TestCase):

    def test_duplicate_skus_are_combined(self):
        rows = [
            {"sku": "COF-1", "qty": 10},
            {"sku": "TEA-2", "qty": 4},
            {"sku": "COF-1", "qty": 5},
        ]
        merged = merge_duplicates(rows)
        by_sku = {row["sku"]: row["qty"] for row in merged}
        self.assertEqual(by_sku, {"COF-1": 15, "TEA-2": 4})

    def test_input_rows_are_not_modified(self):
        """merge_duplicates returns new data; the caller's rows must be
        exactly as they were before the call."""
        rows = [
            {"sku": "COF-1", "qty": 10},
            {"sku": "COF-1", "qty": 5},
        ]
        merge_duplicates(rows)
        self.assertEqual(rows, [
            {"sku": "COF-1", "qty": 10},
            {"sku": "COF-1", "qty": 5},
        ])

    def test_merging_twice_gives_the_same_answer(self):
        """A pure function called twice on the same input must return the
        same result both times."""
        rows = [
            {"sku": "COF-1", "qty": 10},
            {"sku": "COF-1", "qty": 5},
        ]
        first = [dict(row) for row in merge_duplicates(rows)]  # snapshot by value
        second = [dict(row) for row in merge_duplicates(rows)]
        self.assertEqual(first, second)


class TestApplyAdjustments(unittest.TestCase):

    def setUp(self):
        self.rows = [
            {"sku": "COF-1", "qty": 10},
            {"sku": "TEA-2", "qty": 4},
            {"sku": "MUG-3", "qty": 7},
        ]

    def test_adjustment_lands_on_the_matching_row(self):
        apply_adjustments(self.rows, [{"sku": "TEA-2", "delta": 5}])
        self.assertEqual(self.rows[1]["qty"], 9,
                         "TEA-2 must receive its own adjustment")

    def test_other_rows_are_untouched(self):
        apply_adjustments(self.rows, [{"sku": "TEA-2", "delta": 5}])
        self.assertEqual(self.rows[0]["qty"], 10)
        self.assertEqual(self.rows[2]["qty"], 7,
                         "rows that were not adjusted must keep their qty")

    def test_unknown_sku_is_ignored(self):
        apply_adjustments(self.rows, [{"sku": "GHOST-0", "delta": 99}])
        self.assertEqual(total_units(self.rows), 21)


class TestAuditReport(unittest.TestCase):

    def test_end_to_end_total(self):
        raw = [
            "sku,qty",
            "COF-1,10",
            "COF-1,5",
            "TEA-2,4",
            "MUG-3,7",
        ]
        report = audit_report(raw, adjustments=[{"sku": "TEA-2", "delta": -2}])
        self.assertEqual(report["total"], 24)  # 15 + 2 + 7


if __name__ == "__main__":
    unittest.main()
