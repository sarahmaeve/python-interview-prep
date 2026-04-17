"""Tests for UserProfile / AuditEntry / UserDirectory.

Do NOT modify this file.  Fix the bugs in user_profile.py until every
test passes.
"""

import time
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from user_profile import AuditEntry, UserDirectory, UserProfile


class TestUserProfileImmutability(unittest.TestCase):
    """A UserProfile should behave as an immutable value object."""

    def test_assigning_a_field_raises_frozen_instance_error(self):
        profile = UserProfile("u1", "Alice", "alice@example.com")
        with self.assertRaises(FrozenInstanceError):
            profile.display_name = "Mallory"

    def test_frozen_profiles_are_hashable(self):
        """Frozen dataclasses get __hash__ automatically; they must be usable
        as dict keys and set members."""
        # Pin created_at so the two instances are truly identical.
        ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
        a = UserProfile("u1", "Alice", "alice@example.com", created_at=ts)
        b = UserProfile("u1", "Alice", "alice@example.com", created_at=ts)
        # Equal instances hash the same — safe for set deduplication.
        self.assertEqual(hash(a), hash(b))
        self.assertEqual(len({a, b}), 1)


class TestCreatedAtIsPerInstance(unittest.TestCase):
    """created_at must be computed per-instance, not shared across them."""

    def test_two_profiles_created_at_different_times_have_different_timestamps(self):
        a = UserProfile("u1", "Alice", "alice@example.com")
        time.sleep(0.002)
        b = UserProfile("u2", "Bob", "bob@example.com")
        self.assertNotEqual(
            a.created_at, b.created_at,
            "profiles created at different moments should have different "
            "created_at timestamps — otherwise the default was evaluated "
            "once at class definition time, not per instance",
        )

    def test_created_at_is_timezone_aware(self):
        p = UserProfile("u1", "Alice", "alice@example.com")
        self.assertIsNotNone(p.created_at.tzinfo,
                             "created_at must be timezone-aware")

    def test_explicit_created_at_is_respected(self):
        fixed = datetime(2026, 1, 1, tzinfo=timezone.utc)
        p = UserProfile("u1", "Alice", "alice@example.com", created_at=fixed)
        self.assertEqual(p.created_at, fixed)


class TestAuditEntryEquality(unittest.TestCase):
    """AuditEntry equality must ignore the timestamp."""

    def test_same_fields_different_times_compare_equal(self):
        t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        t2 = datetime(2026, 6, 15, tzinfo=timezone.utc)
        a = AuditEntry(actor="alice", action="login", target="/", at=t1)
        b = AuditEntry(actor="alice", action="login", target="/", at=t2)
        self.assertEqual(
            a, b,
            "AuditEntry equality should depend on actor/action/target only",
        )

    def test_list_count_ignores_timestamp(self):
        """list.count uses __eq__; two entries differing only in `at`
        should count as duplicates."""
        t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        t2 = datetime(2026, 6, 15, tzinfo=timezone.utc)
        entries = [
            AuditEntry(actor="alice", action="login", target="/", at=t1),
            AuditEntry(actor="alice", action="login", target="/", at=t2),
            AuditEntry(actor="bob",   action="login", target="/", at=t1),
        ]
        template = AuditEntry("alice", "login", "/", at=t1)
        self.assertEqual(
            entries.count(template), 2,
            "entries differing only in `at` should count as duplicates",
        )

    def test_different_action_compares_unequal(self):
        t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        a = AuditEntry("alice", "login",  "/", at=t)
        b = AuditEntry("alice", "logout", "/", at=t)
        self.assertNotEqual(a, b)


class TestUserDirectory(unittest.TestCase):

    def test_add_and_get_roundtrips(self):
        d = UserDirectory()
        p = UserProfile("u1", "Alice", "alice@example.com")
        d.add(p)
        self.assertEqual(d.get("u1"), p)
        self.assertIsNone(d.get("missing"))

    def test_duplicate_add_raises(self):
        d = UserDirectory()
        p = UserProfile("u1", "Alice", "a@a.com")
        d.add(p)
        with self.assertRaises(ValueError):
            d.add(p)

    def test_all_users_sorted_by_display_name(self):
        d = UserDirectory()
        d.add(UserProfile("u2", "Charlie", "c@c.com"))
        d.add(UserProfile("u1", "Alice", "a@a.com"))
        d.add(UserProfile("u3", "Bob",   "b@b.com"))
        names = [p.display_name for p in d.all_users()]
        self.assertEqual(names, ["Alice", "Bob", "Charlie"])


class TestGrantRoleDoesNotMutateSnapshots(unittest.TestCase):
    """grant_role must produce a NEW profile; previously-retrieved
    references to the profile must remain unchanged."""

    def test_previously_retrieved_profile_is_unchanged(self):
        d = UserDirectory()
        d.add(UserProfile("u1", "Alice", "a@a.com"))

        snapshot = d.get("u1")
        self.assertEqual(snapshot.roles, ())

        d.grant_role("u1", "admin")

        # The caller's snapshot must still show the old roles.
        self.assertEqual(
            snapshot.roles, (),
            "grant_role must not mutate the previously-retrieved profile; "
            "use dataclasses.replace to produce a new instance",
        )

    def test_stored_profile_is_replaced_with_the_granted_role(self):
        d = UserDirectory()
        d.add(UserProfile("u1", "Alice", "a@a.com"))
        d.grant_role("u1", "admin")
        self.assertEqual(d.get("u1").roles, ("admin",))

    def test_grant_role_returns_the_new_profile(self):
        d = UserDirectory()
        d.add(UserProfile("u1", "Alice", "a@a.com"))
        new_profile = d.grant_role("u1", "admin")
        self.assertEqual(new_profile.roles, ("admin",))
        # And it's the same object now stored in the directory.
        self.assertIs(d.get("u1"), new_profile)


if __name__ == "__main__":
    unittest.main()
