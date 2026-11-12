from datetime import datetime, timedelta, timezone

import jwt

from src.config import settings

try:
    # Keeps compatibility with bcrypt hashes created by the previous backend.
    from passlib.context import CryptContext

    _password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(password: str) -> str:
        return _password_context.hash(password)

    def verify_password(password: str, password_hash: str) -> bool:
        try:
            return _password_context.verify(password, password_hash)
        except (ValueError, TypeError):
            return False

except ImportError:
    # Argon2 fallback is useful for minimal environments where passlib is absent.
    from argon2 import PasswordHasher
    from argon2.exceptions import InvalidHashError, VerifyMismatchError, VerificationError

    _password_hasher = PasswordHasher()

    def hash_password(password: str) -> str:
        return _password_hasher.hash(password)

    def verify_password(password: str, password_hash: str) -> bool:
        try:
            return _password_hasher.verify(password_hash, password)
        except (InvalidHashError, VerifyMismatchError, VerificationError):
            return False


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
