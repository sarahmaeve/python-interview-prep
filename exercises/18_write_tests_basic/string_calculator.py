class StringCalculator:
    """A calculator that adds numbers from a delimited string.

    Rules:
    - Empty string returns 0
    - Single number returns that number
    - Numbers separated by commas are summed
    - Newlines between numbers are also valid delimiters (e.g., "1\\n2,3" = 6)
    - Custom delimiter: if the string starts with "//[delimiter]\\n", use that delimiter
      Example: "//;\\n1;2;3" = 6
    - Negative numbers raise ValueError with the message "negatives not allowed: -1, -3"
      (listing ALL negative numbers found)
    - Numbers greater than 1000 are ignored (e.g., "2,1001" = 2)
    """

    def add(self, numbers):
        """Parse the string and return the sum."""
        if not numbers:
            return 0

        delimiter = ","
        if numbers.startswith("//"):
            parts = numbers.split("\n", 1)
            delimiter = parts[0][2:]
            numbers = parts[1]

        numbers = numbers.replace("\n", delimiter)
        num_list = [int(n) for n in numbers.split(delimiter)]

        negatives = [n for n in num_list if n < 0]
        if negatives:
            neg_str = ", ".join(str(n) for n in negatives)
            raise ValueError(f"negatives not allowed: {neg_str}")

        return sum(n for n in num_list if n <= 1000)
