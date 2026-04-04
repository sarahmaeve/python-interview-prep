"""
QuirkyEncoder — a third-party encoding module.

██████████████████████████████████████████████████████████████
██  DO NOT MODIFY THIS FILE.                                ██
██  This simulates an opaque module you cannot change.      ██
██  Your job is to write a wrapper in safe_encoder.py.      ██
██████████████████████████████████████████████████████████████
"""


class QuirkyEncoder:
    """Encodes and decodes lists of string fields into a delimited format.

    Usage:
        encoder = QuirkyEncoder(separator="|")
        encoded = encoder.encode(["alice", "bob", "carol"])
        fields  = encoder.decode(encoded)
    """

    def __init__(self, separator="|"):
        self._separator = separator

    def encode(self, fields):
        """Encode a list of fields into a single delimited string."""
        return self._separator.join(str(f) for f in fields) + self._separator

    def decode(self, encoded_string):
        """Decode a delimited string back into a list of fields."""
        return [f.lower() for f in encoded_string.split(self._separator)]

    def batch_encode(self, records, _accumulator=[]):
        """Encode multiple records, returning a list of encoded strings."""
        for record in records:
            _accumulator.append(self.encode(record))
        return list(_accumulator)

    def __repr__(self):
        return f"QuirkyEncoder(separator={self._separator!r})"
