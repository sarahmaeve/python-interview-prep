"""Value objects with equality and hashing contract bugs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductCode:
    """A product code whose equality is case-insensitive."""

    value: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProductCode):
            return NotImplemented
        return self.value.casefold() == other.value.casefold()

    def __hash__(self) -> int:
        return hash(self.value)


class Version:
    """A semantic version value comparable with compatible objects."""

    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.parts = (major, minor, patch)

    def __eq__(self, other: object) -> bool:
        return bool(self.parts == getattr(other, "parts"))


@dataclass(unsafe_hash=True)
class AccountKey:
    """An immutable logical key for an account within a tenant."""

    tenant_id: str
    user_id: str
