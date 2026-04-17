import hashlib
import hmac


def verify_password(plain: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split("$", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, iterations=260_000)
    return hmac.compare_digest(dk.hex(), dk_hex)