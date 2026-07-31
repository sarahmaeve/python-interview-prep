"""Text reporting for inventories."""

from .models import Inventory


class Reporter:
    """Render inventory item names in a stable order."""

    def render(self, inventory: Inventory) -> str:
        """Return a comma-separated inventory report."""
        return ", ".join(sorted(inventory.items))


def build_report(items: list[str]) -> str:
    """Build an inventory and render its report."""
    return Reporter().render(Inventory(tuple(items)))
