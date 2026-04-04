"""Tests for DataProcessor.

These tests verify both correctness and logging behavior.
Do NOT modify this file. Fix the bugs in data_processor.py.
"""

import unittest

from data_processor import DataProcessor


class TestProcessRecords(unittest.TestCase):
    """Tests for the main processing pipeline."""

    def test_processes_valid_records(self):
        dp = DataProcessor()
        records = [
            {"id": 1, "value": "hello"},
            {"id": 2, "value": "world"},
        ]
        summary = dp.process_records(records)
        self.assertEqual(summary["processed_count"], 2)
        self.assertEqual(summary["error_count"], 0)

    def test_values_are_uppercased(self):
        dp = DataProcessor()
        records = [{"id": 1, "value": "hello"}]
        dp.process_records(records)
        self.assertEqual(dp.processed[0]["value"], "HELLO")

    def test_skips_invalid_records(self):
        dp = DataProcessor()
        records = [
            {"id": 1, "value": "good"},
            {"id": 2},  # missing 'value' key
            {"id": 3, "value": "also good"},
        ]
        summary = dp.process_records(records)
        self.assertEqual(summary["processed_count"], 2)

    def test_skips_non_dict_records(self):
        dp = DataProcessor()
        records = [
            {"id": 1, "value": "good"},
            "not a dict",
            {"id": 3, "value": "also good"},
        ]
        summary = dp.process_records(records)
        self.assertEqual(summary["processed_count"], 2)

    def test_skips_wrong_value_type(self):
        dp = DataProcessor()
        records = [
            {"id": 1, "value": "good"},
            {"id": 2, "value": 42},  # value should be str
        ]
        summary = dp.process_records(records)
        self.assertEqual(summary["processed_count"], 1)

    def test_handles_transform_error(self):
        """A record whose value causes a transform error should be tracked
        as an error, not counted as processed."""
        dp = DataProcessor()
        # value=None passes validation? No — _validate checks isinstance(str).
        # But we can trigger a transform error with a value that passes
        # validation but fails .upper() — this is hard with basic strings,
        # so we test the error tracking path directly:
        # We give a valid record, then verify it's in processed.
        records = [{"id": 1, "value": "hello"}]
        dp.process_records(records)
        self.assertIn("processed_at", dp.processed[0])


class TestLogging(unittest.TestCase):
    """Tests that verify correct log output.

    The processor must log warnings when it skips or fails on records.
    """

    def test_logs_warning_for_missing_keys(self):
        dp = DataProcessor()
        with self.assertLogs("data_processor", level="WARNING") as cm:
            dp.process_records([{"id": 1}])  # missing 'value'

        # At least one warning about the skipped record
        self.assertTrue(
            any("missing" in msg.lower() or "skip" in msg.lower()
                for msg in cm.output),
            f"Expected a warning about skipped record, got: {cm.output}"
        )

    def test_logs_warning_for_non_dict(self):
        dp = DataProcessor()
        with self.assertLogs("data_processor", level="WARNING") as cm:
            dp.process_records(["not a dict"])

        self.assertTrue(
            any("non-dict" in msg.lower() or "skip" in msg.lower() or "dict" in msg.lower()
                for msg in cm.output),
            f"Expected a warning about non-dict record, got: {cm.output}"
        )

    def test_logs_warning_for_wrong_value_type(self):
        dp = DataProcessor()
        with self.assertLogs("data_processor", level="WARNING") as cm:
            dp.process_records([{"id": 1, "value": 42}])

        self.assertTrue(
            any("int" in msg.lower() or "type" in msg.lower() or "skip" in msg.lower()
                for msg in cm.output),
            f"Expected a warning about wrong type, got: {cm.output}"
        )

    def test_no_warning_for_valid_records(self):
        """Valid records should NOT produce any warnings."""
        dp = DataProcessor()
        # assertLogs raises AssertionError if no logs are captured.
        # We expect NO warnings, so assertLogs should fail.
        with self.assertRaises(AssertionError):
            with self.assertLogs("data_processor", level="WARNING"):
                dp.process_records([{"id": 1, "value": "hello"}])


class TestSummary(unittest.TestCase):
    """Tests for the get_summary() method."""

    def test_summary_counts_only_successful(self):
        """processed_count must NOT include records that failed transform."""
        dp = DataProcessor()
        records = [
            {"id": 1, "value": "hello"},
            {"id": 2, "value": "world"},
        ]
        summary = dp.process_records(records)
        # Both records are valid and transform successfully
        self.assertEqual(summary["processed_count"], 2)

    def test_summary_error_ids(self):
        """error_ids should contain IDs of records that failed."""
        dp = DataProcessor()
        # All valid records — no errors expected
        records = [{"id": 1, "value": "hello"}]
        summary = dp.process_records(records)
        self.assertEqual(summary["error_ids"], [])

    def test_summary_empty_input(self):
        dp = DataProcessor()
        summary = dp.process_records([])
        self.assertEqual(summary["processed_count"], 0)
        self.assertEqual(summary["error_count"], 0)
        self.assertEqual(summary["error_ids"], [])

    def test_summary_mixed_valid_and_invalid(self):
        """Invalid records should not appear in processed_count."""
        dp = DataProcessor()
        records = [
            {"id": 1, "value": "good"},
            "bad record",
            {"id": 3},  # missing value
            {"id": 4, "value": "also good"},
        ]
        # Only records 1 and 4 are valid
        with self.assertLogs("data_processor", level="WARNING"):
            summary = dp.process_records(records)
        self.assertEqual(summary["processed_count"], 2)


class TestTransform(unittest.TestCase):
    """Tests for the _transform() method's behavior."""

    def test_transform_uppercases_value(self):
        dp = DataProcessor()
        records = [{"id": 1, "value": "hello world"}]
        dp.process_records(records)
        self.assertEqual(dp.processed[0]["value"], "HELLO WORLD")

    def test_transform_adds_timestamp(self):
        dp = DataProcessor()
        records = [{"id": 1, "value": "test"}]
        dp.process_records(records)
        self.assertIn("processed_at", dp.processed[0])
        # Timestamp should be an ISO format string
        self.assertIsInstance(dp.processed[0]["processed_at"], str)


if __name__ == "__main__":
    unittest.main()
