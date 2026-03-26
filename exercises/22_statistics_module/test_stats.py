import unittest
from stats import mean, median, mode, std_dev, percentile


class TestMean(unittest.TestCase):

    def test_basic_list(self):
        """mean of [1, 2, 3, 4, 5] is 3.0."""
        self.assertEqual(mean([1, 2, 3, 4, 5]), 3.0)

    def test_single_element(self):
        """mean of a single-element list is that element."""
        self.assertEqual(mean([42]), 42.0)

    def test_empty_raises_value_error(self):
        """mean of an empty list raises ValueError."""
        with self.assertRaises(ValueError):
            mean([])


class TestMedian(unittest.TestCase):

    def test_odd_length(self):
        """median of an odd-length list is the middle element when sorted."""
        self.assertEqual(median([3, 1, 2]), 2)

    def test_even_length(self):
        """median of an even-length list is the average of the two middle values."""
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_does_not_modify_input(self):
        """median must not mutate the original list."""
        numbers = [3, 1, 2]
        median(numbers)
        self.assertEqual(numbers, [3, 1, 2])

    def test_empty_raises_value_error(self):
        """median of an empty list raises ValueError."""
        with self.assertRaises(ValueError):
            median([])


class TestMode(unittest.TestCase):

    def test_single_mode(self):
        """mode returns the most frequently occurring value."""
        self.assertEqual(mode([1, 2, 2, 3]), 2)

    def test_tie_returns_smallest(self):
        """when multiple values tie for most frequent, return the smallest."""
        self.assertEqual(mode([1, 1, 2, 2, 3]), 1)

    def test_empty_raises_value_error(self):
        """mode of an empty list raises ValueError."""
        with self.assertRaises(ValueError):
            mode([])


class TestStdDev(unittest.TestCase):

    def test_basic_population_std_dev(self):
        """population std_dev of [2, 4, 4, 4, 5, 5, 7, 9] is 2.0."""
        self.assertAlmostEqual(std_dev([2, 4, 4, 4, 5, 5, 7, 9]), 2.0)

    def test_identical_values_returns_zero(self):
        """std_dev of a list of identical values is 0.0."""
        self.assertEqual(std_dev([5, 5, 5]), 0.0)

    def test_single_element_returns_zero(self):
        """std_dev of a single-element list is 0.0."""
        self.assertEqual(std_dev([7]), 0.0)


class TestPercentile(unittest.TestCase):

    def test_50th_percentile_equals_median(self):
        """50th percentile of [1, 2, 3, 4, 5] is 3.0 (the median)."""
        self.assertAlmostEqual(percentile([1, 2, 3, 4, 5], 50), 3.0)

    def test_0th_percentile_is_minimum(self):
        """0th percentile is the minimum value in the list."""
        numbers = [3, 1, 4, 1, 5, 9, 2, 6]
        self.assertEqual(percentile(numbers, 0), min(numbers))

    def test_invalid_p_raises_value_error(self):
        """p outside [0, 100] raises ValueError."""
        with self.assertRaises(ValueError):
            percentile([1, 2, 3], -1)
        with self.assertRaises(ValueError):
            percentile([1, 2, 3], 101)


if __name__ == "__main__":
    unittest.main()
