import hashlib
import os


def hash_password(plain: str) -> str:
    """PBKDF2-HMAC-SHA256 with a random 16-byte salt. Returns 'salt$hash' (hex)."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, iterations=260_000)
    return f"{salt.hex()}${dk.hex()}"