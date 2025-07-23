import secrets
import string


def generate_random_string(length: int = 16) -> str:
    """Generate a cryptographically secure random string.

    Args:
        length: Length of the string to generate

    Returns:
        Random string containing letters and digits

    Note:
        This function is deprecated. Use app.utils.generate_random_string instead.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure token for sessions or API keys.

    Args:
        length: Length of the token to generate

    Returns:
        Secure random token
    """
    return secrets.token_urlsafe(length)


def generate_file_key(length: int = 16) -> str:
    """Generate a key for file naming.

    Args:
        length: Length of the key to generate

    Returns:
        Random string suitable for file naming
    """
    return generate_random_string(length)
