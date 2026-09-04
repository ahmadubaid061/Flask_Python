import secrets
import hashlib


def generate_login_code() -> str:
    """A 6-digit code, e.g. '048213'. Zero-padded so it's always 6 digits."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_code(code: str) -> str:
    """We never store the raw code — only its hash, so a leaked database
    row can't be used to log in."""
    return hashlib.sha256(code.encode()).hexdigest()


def generate_device_token() -> str:
    """A long random token stored in the trusted-device cookie and mirrored
    in the TrustedDevice table."""
    return secrets.token_urlsafe(48)
