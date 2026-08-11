import asyncio
import logging
import re
from datetime import datetime, timezone, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import (
    HashingError,
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
)
from itsdangerous import URLSafeSerializer

from src.config import app_config

ISSUER = "book-platform"
AUDIENCE = "book-platform-api"

ph = PasswordHasher()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ------ Password ------
def validate_password_strength(value: str) -> str:
    value = str(value)
    if len(value) < 8:
        raise ValueError("Password must have at least 8 characters")
    if not any(c.isupper() for c in value):
        raise ValueError("Password must have at least one uppercase letter")
    if not any(c.islower() for c in value):
        raise ValueError("Password must have at least one lowercase letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must have at least one digit")
    return value


async def hash_password(input_password: str):
    try:
        return await asyncio.to_thread(
            ph.hash, password=input_password, salt=bytes(app_config.JWT_SALT, "utf-8")
        )
    except HashingError as e:
        logging.exception(e)
        return None


async def verify_password(input_password: str, hashed_password: str):
    try:
        return await asyncio.to_thread(ph.verify, hashed_password, input_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError) as e:
        logging.exception(e)
        return False


# ------ JWT ------
def create_jwt_token(user_id: str, role: str, jti: str, refresh: bool = False):

    now = utcnow()

    if refresh:
        expiry = now + timedelta(days=app_config.JWT_REFRESH_TOKEN_EXPIRY_DAYS)
    else:
        expiry = now + timedelta(seconds=app_config.JWT_ACCESS_TOKEN_EXPIRY_SECONDS)

    payload = {
        "sub": user_id,
        "exp": expiry,
        "iat": now,
        "nbf": now,
        "jti": jti,
        "refresh": refresh,
        "aud": AUDIENCE,
        "iss": ISSUER,
        "role": role,
    }

    try:
        token = jwt.encode(
            key=app_config.JWT_SECRET,
            payload=payload,
            algorithm=app_config.JWT_ALGORITHM,
        )
        return token

    except ValueError as e:
        logging.exception(e)
        return None


def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=app_config.JWT_SECRET,
            algorithms=[app_config.JWT_ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"require": ["sub", "exp", "iat", "nbf", "jti", "refresh"]},
        )
        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


# ------ Custom Validators ------
def validate_username(username: str) -> str:
    username = username.strip()

    if len(username) < 3 or len(username) > 20:
        raise ValueError("Username must be between 3 and 20 characters")

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        raise ValueError("Username can only contain letters, numbers, and underscores")

    if username[0].isdigit():
        raise ValueError("Username cannot start with a number")

    if "__" in username:
        raise ValueError("Username cannot contain consecutive underscores")

    return username.lower()  # normalize to lowercase for consistent uniqueness checks


# ------- Verification -------
verifier = URLSafeSerializer(
    secret_key=app_config.VERIFICATION_SECRET, salt=app_config.VERIFICATION_SALT
)


def generate_verification_token(email: str, username: str):
    token = verifier.dumps({"email": email, "username": username})

    return token


def validate_verification_token(token: str) -> dict | None:
    try:
        result = verifier.loads(token)
        return result

    except Exception as e:
        logging.exception(e)
        return None
