"""Product catalog with case-insensitive SKU lookup.

Part of exercise 33 (capstone) — see README.md.
"""


class Catalog:
    """Stores products keyed by SKU.

    SKU lookup is case-INsensitive: "cof-1", "COF-1" and "Cof-1" all
    refer to the same product.  Internally, keys are stored upper-case.
    """

    def __init__(self):
        self._by_sku = {}

    def register(self, product):
        """Add *product* to the catalog (replacing any same-SKU entry)."""
        self._by_sku[product.sku.upper()] = product

    def get(self, sku):
        """Return the Product for *sku* (any casing), or None if unknown."""
        return self._by_sku.get(sku)

    def skus(self):
        """All registered SKUs, in normalised (upper-case) form."""
        return sorted(self._by_sku)

    def __len__(self):
        return len(self._by_sku)
