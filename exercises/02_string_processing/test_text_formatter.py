import unittest
from text_formatter import title_case, truncate, word_wrap


class TestTitleCase(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(title_case("hello world"), "Hello World")

    def test_mixed_case_input(self):
        self.assertEqual(title_case("hELLO wORLD"), "Hello World")

    def test_single_word(self):
        self.assertEqual(title_case("python"), "Python")

    def test_empty_string(self):
        self.assertEqual(title_case(""), "")


class TestTruncate(unittest.TestCase):
    def test_long_string(self):
        self.assertEqual(truncate("Hello, World!", 10), "Hello, ...")

    def test_string_within_limit(self):
        self.assertEqual(truncate("Hi", 10), "Hi")

    def test_exact_length(self):
        self.assertEqual(truncate("Hello", 5), "Hello")

    def test_result_length_does_not_exceed_max(self):
        result = truncate("This is a long sentence that must be cut.", 20)
        self.assertLessEqual(len(result), 20)
        self.assertTrue(result.endswith("..."))


class TestWordWrap(unittest.TestCase):
    def test_short_text_no_wrap(self):
        self.assertEqual(word_wrap("hello", 10), "hello")

    def test_wraps_at_word_boundary(self):
        result = word_wrap("one two three", 7)
        lines = result.split("\n")
        self.assertEqual(lines[0], "one two")
        self.assertEqual(lines[1], "three")

    def test_no_leading_spaces_on_wrapped_lines(self):
        result = word_wrap("aaa bbb ccc ddd", 7)
        for line in result.split("\n"):
            self.assertEqual(line, line.lstrip(), f"Leading space found: {line!r}")

    def test_single_long_word(self):
        result = word_wrap("abcdefghij", 5)
        self.assertEqual(result, "abcdefghij")


if __name__ == "__main__":
    unittest.main()
