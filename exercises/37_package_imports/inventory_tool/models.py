"""Domain models for inventory reporting."""

from dataclasses import dataclass

from .reporting import Reporter


@dataclass(frozen=True)
class Inventory:
    """A collection of item names."""

    items: tuple[str, ...]

    def render(self, reporter: Reporter) -> str:
        """Render this inventory with the supplied reporter."""
        return reporter.render(self)
