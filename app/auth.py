import os
import hashlib
import base64
import hmac


def _hash_password_raw(plain_password: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """
    Internal helper that derives a key from the password using PBKDF2-HMAC-SHA256.
    """
    return hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        iterations,
    )


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using PBKDF2-HMAC-SHA256.

    Stored format: iterations$salt_base64$hash_base64
    """
    iterations = 100_000
    salt = os.urandom(16)
    dk = _hash_password_raw(plain_password, salt, iterations)

    salt_b64 = base64.b64encode(salt).decode("utf-8")
    dk_b64 = base64.b64encode(dk).decode("utf-8")

    return f"{iterations}${salt_b64}${dk_b64}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches the stored hash.
    """
    try:
        iterations_str, salt_b64, dk_b64 = hashed_password.split("$")
        iterations = int(iterations_str)
        salt = base64.b64decode(salt_b64.encode("utf-8"))
        expected_dk = base64.b64decode(dk_b64.encode("utf-8"))
    except Exception:
        # Malformed hash string
        return False

    actual_dk = _hash_password_raw(plain_password, salt, iterations)

    # Use constant-time comparison
    return hmac.compare_digest(actual_dk, expected_dk)
