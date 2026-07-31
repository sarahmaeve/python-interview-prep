"""Tests for equality, hashing, and key stability."""

import unittest
from dataclasses import FrozenInstanceError

from value_objects import AccountKey, ProductCode, Version


class TestProductCode(unittest.TestCase):
    def test_equal_codes_have_equal_hashes(self):
        lower = ProductCode("sku-42")
        upper = ProductCode("SKU-42")

        self.assertEqual(lower, upper)
        self.assertEqual(hash(lower), hash(upper))

    def test_set_deduplicates_equivalent_codes(self):
        codes = {ProductCode("sku-42"), ProductCode("SKU-42")}

        self.assertEqual(codes, {ProductCode("Sku-42")})


class CompatibleVersion:
    def __init__(self, parts: tuple[int, int, int]) -> None:
        self._parts = parts

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._parts == other.parts
        return NotImplemented


class TestVersion(unittest.TestCase):
    def test_foreign_object_compares_unequal(self):
        self.assertNotEqual(Version(3, 11, 0), object())

    def test_reflected_comparison_gets_an_opportunity(self):
        version = Version(3, 11, 0)
        compatible = CompatibleVersion((3, 11, 0))

        self.assertTrue(version == compatible)

    def test_versions_compare_by_parts(self):
        self.assertEqual(Version(3, 11, 0), Version(3, 11, 0))
        self.assertNotEqual(Version(3, 11, 0), Version(3, 12, 0))


class TestAccountKey(unittest.TestCase):
    def test_key_fields_cannot_change(self):
        key = AccountKey("tenant-a", "user-7")

        with self.assertRaises(FrozenInstanceError):
            key.user_id = "user-8"

    def test_equivalent_key_retrieves_dictionary_value(self):
        accounts = {AccountKey("tenant-a", "user-7"): "active"}

        self.assertEqual(accounts[AccountKey("tenant-a", "user-7")], "active")


if __name__ == "__main__":
    unittest.main()
