"""Tests for the student grade processing pipeline."""

import unittest

from grade_processor import (
    StudentRecord,
    calculate_gpa,
    format_transcript,
    get_honor_roll,
    merge_records,
    parse_records,
)


class TestParseRecords(unittest.TestCase):
    def test_parses_multiple_records(self):
        raw = [
            {"name": "Alice", "student_id": 1001, "grades": {"Math": 3.8}},
            {"name": "Bob", "student_id": 1002, "grades": {"Math": 3.2}},
        ]
        records = parse_records(raw)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].name, "Alice")

    def test_student_id_is_string(self):
        """student_id must be stored as a str so string methods work."""
        raw = [{"name": "Alice", "student_id": 1001, "grades": {}}]
        records = parse_records(raw)
        self.assertIsInstance(records[0].student_id, str)


class TestCalculateGPA(unittest.TestCase):
    def test_normal_gpa(self):
        record = StudentRecord("Alice", "1001", {"Math": 3.8, "English": 3.6})
        self.assertAlmostEqual(calculate_gpa(record), 3.7)

    def test_single_course(self):
        record = StudentRecord("Bob", "1002", {"History": 4.0})
        self.assertAlmostEqual(calculate_gpa(record), 4.0)

    def test_empty_grades_returns_zero(self):
        """An empty grades dict should yield 0.0, not None."""
        record = StudentRecord("Carol", "1003", {})
        result = calculate_gpa(record)
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, 0.0)


class TestGetHonorRoll(unittest.TestCase):
    def test_some_qualify(self):
        records = [
            StudentRecord("Alice", "1001", {"Math": 3.8, "English": 3.6}),
            StudentRecord("Bob", "1002", {"Math": 2.9}),
        ]
        result = get_honor_roll(records)
        self.assertEqual(result, ["Alice"])

    def test_none_qualify_returns_empty_list(self):
        """Should return [] when nobody qualifies, not None."""
        records = [
            StudentRecord("Bob", "1002", {"Math": 2.5}),
        ]
        result = get_honor_roll(records, min_gpa=3.5)
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

    def test_honor_roll_is_iterable(self):
        """Callers must be able to iterate over the result in all cases."""
        records = [
            StudentRecord("Bob", "1002", {"Math": 2.5}),
        ]
        result = get_honor_roll(records)
        # This would raise TypeError if result is None
        names = [name for name in result]
        self.assertEqual(names, [])


class TestMergeRecords(unittest.TestCase):
    def test_merge_combines_grades(self):
        r1 = StudentRecord("Alice", "1001", {"Math": 3.8})
        r2 = StudentRecord("Alice", "1001", {"English": 3.6})
        merged = merge_records(r1, r2)
        self.assertEqual(merged.grades, {"Math": 3.8, "English": 3.6})

    def test_merged_grades_is_dict(self):
        """Grades must remain a dict after merging."""
        r1 = StudentRecord("Alice", "1001", {"Math": 3.8})
        r2 = StudentRecord("Alice", "1001", {"English": 3.6})
        merged = merge_records(r1, r2)
        self.assertIsInstance(merged.grades, dict)


class TestFormatTranscript(unittest.TestCase):
    def test_basic_transcript(self):
        record = StudentRecord("Alice", "1001", {"Math": 3.8})
        text = format_transcript(record)
        self.assertIn("Alice", text)
        self.assertIn("1001", text)
        self.assertIn("Math", text)
        self.assertIn("3.8", text)

    def test_transcript_after_merge(self):
        """format_transcript must work on merged records."""
        r1 = StudentRecord("Alice", "1001", {"Math": 3.8})
        r2 = StudentRecord("Alice", "1001", {"English": 3.6})
        merged = merge_records(r1, r2)
        text = format_transcript(merged)
        self.assertIn("Math", text)
        self.assertIn("English", text)


if __name__ == "__main__":
    unittest.main()
