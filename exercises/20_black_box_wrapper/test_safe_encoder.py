"""Tests for SafeEncoder — the wrapper around QuirkyEncoder.

These tests define the CORRECT behavior of SafeEncoder.
Do NOT modify this file. Fix the bugs in safe_encoder.py.
"""

import unittest

from safe_encoder import SafeEncoder


class TestSafeEncoderEncode(unittest.TestCase):
    """Tests for the encode() method."""

    def setUp(self):
        self.encoder = SafeEncoder(separator="|")

    def test_encode_basic_fields(self):
        result = self.encoder.encode(["alice", "bob", "carol"])
        self.assertEqual(result, "alice|bob|carol")

    def test_encode_no_trailing_separator(self):
        result = self.encoder.encode(["x", "y"])
        self.assertFalse(result.endswith("|"),
                         f"Result should not end with separator: {result!r}")

    def test_encode_single_field(self):
        result = self.encoder.encode(["hello"])
        self.assertEqual(result, "hello")

    def test_encode_rejects_none(self):
        with self.assertRaises(TypeError):
            self.encoder.encode(["alice", None, "carol"])

    def test_encode_rejects_none_only(self):
        with self.assertRaises(TypeError):
            self.encoder.encode([None])

    def test_encode_accepts_strings(self):
        # Should NOT raise for valid string fields
        result = self.encoder.encode(["hello", "world"])
        self.assertEqual(result, "hello|world")

    def test_encode_converts_numbers_to_strings(self):
        result = self.encoder.encode([1, 2.5, "three"])
        self.assertEqual(result, "1|2.5|three")

    def test_encode_custom_separator(self):
        encoder = SafeEncoder(separator=",")
        result = encoder.encode(["a", "b", "c"])
        self.assertEqual(result, "a,b,c")


class TestSafeEncoderDecode(unittest.TestCase):
    """Tests for the decode() method."""

    def setUp(self):
        self.encoder = SafeEncoder(separator="|")

    def test_decode_basic(self):
        result = self.encoder.decode("alice|bob|carol")
        self.assertEqual(result, ["alice", "bob", "carol"])

    def test_decode_preserves_case(self):
        result = self.encoder.decode("Alice|Bob|CAROL")
        self.assertEqual(result, ["Alice", "Bob", "CAROL"])

    def test_decode_single_field(self):
        result = self.encoder.decode("hello")
        self.assertEqual(result, ["hello"])


class TestSafeEncoderBatchEncode(unittest.TestCase):
    """Tests for the batch_encode() method."""

    def setUp(self):
        self.encoder = SafeEncoder(separator="|")

    def test_batch_encode_multiple_records(self):
        records = [["a", "b"], ["c", "d"]]
        result = self.encoder.batch_encode(records)
        self.assertEqual(result, ["a|b", "c|d"])

    def test_batch_encode_independent_calls(self):
        """Two sequential batch_encode calls must return independent results.

        This test catches mutable default argument contamination.
        """
        first = self.encoder.batch_encode([["a", "b"]])
        second = self.encoder.batch_encode([["c", "d"]])
        self.assertEqual(first, ["a|b"])
        self.assertEqual(second, ["c|d"])

    def test_batch_encode_empty(self):
        result = self.encoder.batch_encode([])
        self.assertEqual(result, [])


class TestSafeEncoderRoundTrip(unittest.TestCase):
    """Tests for the round_trip() method."""

    def setUp(self):
        self.encoder = SafeEncoder(separator="|")

    def test_round_trip_preserves_fields(self):
        fields = ["Alice", "Bob", "Carol"]
        result = self.encoder.round_trip(fields)
        self.assertEqual(result, ["Alice", "Bob", "Carol"])

    def test_round_trip_with_numbers(self):
        fields = ["1", "2", "3"]
        result = self.encoder.round_trip(fields)
        self.assertEqual(result, ["1", "2", "3"])

    def test_round_trip_single_field(self):
        result = self.encoder.round_trip(["hello"])
        self.assertEqual(result, ["hello"])


if __name__ == "__main__":
    unittest.main()
