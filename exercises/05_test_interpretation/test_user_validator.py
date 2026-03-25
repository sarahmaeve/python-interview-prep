import unittest
from user_validator import validate_email, validate_password, validate_username, validate_user


class TestValidateEmail(unittest.TestCase):

    def test_valid_email_with_dot_after_at(self):
        self.assertTrue(validate_email("alice@example.com"))

    def test_valid_email_with_subdomain(self):
        self.assertTrue(validate_email("bob@mail.example.org"))

    def test_rejects_email_without_at_symbol(self):
        self.assertFalse(validate_email("aliceexample.com"))

    def test_rejects_email_with_at_but_no_dot_in_domain(self):
        """The domain part (after @) must contain at least one dot."""
        self.assertFalse(validate_email("user@domain"))


class TestValidatePassword(unittest.TestCase):

    def test_valid_password_longer_than_eight(self):
        self.assertTrue(validate_password("securepass1"))

    def test_valid_password_exactly_eight_characters(self):
        """A password with exactly 8 characters and a digit is valid."""
        self.assertTrue(validate_password("passwor1"))

    def test_rejects_password_with_seven_characters(self):
        self.assertFalse(validate_password("pass1ab"))

    def test_rejects_password_without_digit(self):
        self.assertFalse(validate_password("abcdefghij"))


class TestValidateUsername(unittest.TestCase):

    def test_valid_username_starting_with_letter(self):
        self.assertTrue(validate_username("alice123"))

    def test_rejects_username_starting_with_digit(self):
        """Usernames must start with a letter, not a digit."""
        self.assertFalse(validate_username("1alice"))

    def test_rejects_username_shorter_than_three(self):
        self.assertFalse(validate_username("ab"))

    def test_rejects_username_with_special_characters(self):
        self.assertFalse(validate_username("alice!@#"))


class TestValidateUser(unittest.TestCase):

    def test_valid_user_dict_passes(self):
        user = {
            "email": "alice@example.com",
            "password": "securepass1",
            "username": "alice123",
        }
        self.assertTrue(validate_user(user))

    def test_raises_value_error_when_required_field_missing(self):
        """validate_user must raise ValueError (not swallow exceptions)
        when a required field like 'email' is missing from the dict."""
        user = {"password": "securepass1", "username": "alice123"}
        with self.assertRaises(ValueError) as ctx:
            validate_user(user)
        self.assertIn("email", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
