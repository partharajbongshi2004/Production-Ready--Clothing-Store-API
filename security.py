import hashlib
import hmac
import re
from typing import Tuple

# Pre-computed SHA-256 hash for default password 'admin123'
DEFAULT_ADMIN_HASH = hashlib.sha256("admin123".encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """Return the SHA-256 hexadecimal digest of a plaintext password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_admin_password(password: str) -> bool:
    """Securely verify the admin password using constant-time comparison."""
    if not password:
        return False
    input_hash = hash_password(password)
    return hmac.compare_digest(input_hash, DEFAULT_ADMIN_HASH)


def validate_product_input(
    name: str, color: str, price: float, stock: int
) -> Tuple[bool, str]:
    """
    Validate clothing product inputs before database insertion.
    Returns (is_valid, error_message).
    """
    cleaned_name = name.strip()
    cleaned_color = color.strip()

    if not cleaned_name or len(cleaned_name) < 2:
        return False, "Product name must be at least 2 characters long."

    if len(cleaned_name) > 100:
        return False, "Product name cannot exceed 100 characters."

    if not cleaned_color or not re.match(r"^[A-Za-z0-9\s\-/]+$", cleaned_color):
        return False, "Color must contain valid letters, numbers, or spaces."

    if price is None or price <= 0:
        return False, "Price must be greater than 0."

    if stock is None or stock < 0 or not isinstance(stock, int):
        return False, "Stock quantity must be a non-negative integer (0 or more)."

    return True, ""
