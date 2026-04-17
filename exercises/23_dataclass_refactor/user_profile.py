"""UserProfile — a dataclass-shaped module with 4 bugs for you to find and fix.

The code already uses @dataclass, but not with the right flags, and some
methods don't respect the immutability intent.

Your job:
  - Find and fix 4 bugs.
  - All tests must pass without modification.

Everything you need is covered in:
  - guides/02_classes_and_oop.py (Section 9)
  - guides/09_modern_data_types.py
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# A UserProfile is a VALUE OBJECT.  Callers treat it as immutable: two
# profiles with identical fields are interchangeable, and nobody should
# be able to silently mutate one and affect code that holds a reference.
#
# The `roles` field is a tuple because profiles are immutable; granting a
# role produces a new profile rather than mutating the old one.
# ---------------------------------------------------------------------------


@dataclass
class UserProfile:
    """A user's profile.  Shared across the system."""

    user_id: str
    display_name: str
    email: str
    roles: tuple[str, ...] = ()
    created_at: datetime = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# An audit log entry.  Entries are appended only, never mutated.
#
# Two entries with the same actor, action, and target should compare
# equal — the wall-clock timestamp is informational, not identity.
# Callers de-duplicate audit entries with `set(entries)` and rely on
# this equality semantics.
# ---------------------------------------------------------------------------


@dataclass
class AuditEntry:
    """One line in the audit log."""

    actor: str
    action: str
    target: str
    at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# The user directory keeps users indexed by id.  Because profiles are
# immutable, granting a role must produce a NEW profile and replace the
# stored one; any previously-retrieved reference must remain unchanged.
# ---------------------------------------------------------------------------


class UserDirectory:
    def __init__(self) -> None:
        self._users: dict[str, UserProfile] = {}

    def add(self, profile: UserProfile) -> None:
        if profile.user_id in self._users:
            raise ValueError(f"duplicate user_id: {profile.user_id}")
        self._users[profile.user_id] = profile

    def get(self, user_id: str) -> UserProfile | None:
        return self._users.get(user_id)

    def all_users(self) -> list[UserProfile]:
        """Return every profile, sorted by display_name."""
        return sorted(self._users.values(), key=lambda u: u.display_name)

    def grant_role(self, user_id: str, role: str) -> UserProfile:
        """Grant *role* to *user_id* and return the new profile.

        A caller that previously retrieved the profile must still see
        their old snapshot — only the directory's stored reference is
        replaced.
        """
        profile = self._users[user_id]
        profile.roles += (role,)
        return profile
