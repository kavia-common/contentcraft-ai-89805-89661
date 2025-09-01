from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict

import hashlib
import hmac
import os
import base64
import json

from ..core.config import settings


def _pbkdf2_sha256(password: str, salt: bytes, iterations: int = 260000) -> str:
    """Derive a PBKDF2-SHA256 hash for a password and salt."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return base64.b64encode(dk).decode("utf-8")


def hash_password(password: str) -> str:
    """Hash a password with a random salt."""
    salt = os.urandom(16)
    digest = _pbkdf2_sha256(password, salt)
    return f"pbkdf2_sha256${base64.b64encode(salt).decode()}${digest}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored hash."""
    try:
        algo, salt_b64, stored_dk_b64 = hashed_password.split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        computed = _pbkdf2_sha256(plain_password, salt)
        return hmac.compare_digest(computed, stored_dk_b64)
    except Exception:
        return False


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    rem = len(data) % 4
    if rem:
        data += "=" * (4 - rem)
    return base64.urlsafe_b64decode(data.encode("utf-8"))


def _jwt_sign(header: Dict[str, Any], payload: Dict[str, Any], secret: str) -> str:
    header_b64 = _b64url(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def _jwt_verify(token: str, secret: str) -> Optional[Dict[str, Any]]:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url(expected_sig), sig_b64):
            return None
        payload = json.loads(_b64url_decode(payload_b64))
        # Expiry check
        if "exp" in payload:
            if datetime.now(timezone.utc).timestamp() > payload["exp"]:
                return None
        return payload
    except Exception:
        return None


# PUBLIC_INTERFACE
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token.

    Args:
        subject: unique identifier (e.g., user id or email)
        expires_delta: timedelta until expiration

    Returns:
        str: encoded JWT token
    """
    header = {"alg": settings.ALGORITHM, "typ": "JWT"}
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    return _jwt_sign(header, payload, settings.SECRET_KEY)


# PUBLIC_INTERFACE
def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT token.

    Args:
        token: JWT string

    Returns:
        Optional dict with payload if valid, else None.
    """
    return _jwt_verify(token, settings.SECRET_KEY)
