import os
import secrets
import string
from typing import Optional
from werkzeug.utils import secure_filename
from flask import current_app, request


def generate_random_string(length: int = 16) -> str:
    """Generate a cryptographically secure random string.

    Args:
        length: Length of the string to generate

    Returns:
        Random string containing letters and digits
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed.

    Args:
        filename: The filename to check

    Returns:
        True if file extension is allowed, False otherwise
    """
    if not filename or '.' not in filename:
        return False

    extension = filename.rsplit('.', 1)[1].lower()
    return extension in current_app.config['ALLOWED_EXTENSIONS']


def validate_file_size() -> bool:
    """Validate if the uploaded file size is within limits.

    Returns:
        True if file size is valid, False otherwise
    """
    content_length = request.content_length
    if content_length is None:
        return False
    return content_length <= current_app.config['MAX_CONTENT_LENGTH']


def generate_filename(original_filename: str) -> str:
    """Generate a secure filename with random prefix.

    Args:
        original_filename: The original filename

    Returns:
        Secure filename with random prefix
    """
    key = generate_random_string()
    safe_filename = secure_filename(original_filename)
    return f"{key}_{safe_filename}"


def ensure_upload_directory() -> None:
    """Ensure the upload directory exists."""
    upload_path = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_path, exist_ok=True)


def get_file_size_mb(size_bytes: int) -> float:
    """Convert bytes to megabytes.

    Args:
        size_bytes: Size in bytes

    Returns:
        Size in megabytes rounded to 2 decimal places
    """
    return round(size_bytes / (1024 * 1024), 2)


def create_file_url(filename: str) -> str:
    """Create the complete URL for a file.

    Args:
        filename: The filename

    Returns:
        Complete URL to access the file
    """
    base_url = current_app.config['BASE_URL']
    return f"{base_url}/media/uploads/{filename}"
