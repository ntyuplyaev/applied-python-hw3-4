import secrets
import string
from datetime import datetime, timedelta


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def handle_expiration(expires_at: datetime or None) -> datetime:
    if not expires_at:
        return datetime.utcnow() + timedelta(days=90)

    if expires_at.time() == datetime.min.time():
        return expires_at.replace(
            hour=23,
            minute=59,
            second=59
        ) + timedelta(days=90)

    return expires_at
