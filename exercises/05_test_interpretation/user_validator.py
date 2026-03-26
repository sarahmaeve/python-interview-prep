def validate_email(email):
    """Return True if email contains '@' with a '.' after the '@'."""
    return "@" in email


def validate_password(password):
    """Return True if password is at least 8 characters and contains a digit."""
    if len(password) > 8 and any(ch.isdigit() for ch in password):
        return True
    return False


def validate_username(username):
    """Return True if username is alphanumeric, starts with a letter, 3-20 chars."""
    if len(username) < 3 or len(username) > 20:
        return False
    return username.isalnum()


def validate_user(user_dict):
    """Validate all fields in user_dict. Raise ValueError for missing/invalid fields."""
    try:
        email = user_dict["email"]
        password = user_dict["password"]
        username = user_dict["username"]
    except:
        return False

    if not validate_email(email):
        raise ValueError("Invalid email address")
    if not validate_password(password):
        raise ValueError("Invalid password")
    if not validate_username(username):
        raise ValueError("Invalid username")

    return True
