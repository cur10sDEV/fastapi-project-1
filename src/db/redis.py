from datetime import timedelta
from enum import StrEnum

from redis.asyncio import Redis

from src.config import app_config

r = Redis(
    host=app_config.REDIS_HOST,
    port=app_config.REDIS_PORT,
    decode_responses=True,
)


class RedisKeysPrefixes(StrEnum):
    REFRESH_TOKEN = "refresh_token"
    USER_VERIFICATION_TOKEN = "user_verification_token"
    PASSWORD_RESET_TOKEN = "password_reset_token"


async def get_redis():
    return await r


async def check_refresh_token_jti(token_jti: str, user_id: str):
    stored_user_id = await r.get(f"{RedisKeysPrefixes.REFRESH_TOKEN}:{token_jti}")
    return stored_user_id == user_id


async def set_refresh_token_jti(token_jti: str, user_id: str):
    return await r.set(
        f"refresh_token:{token_jti}",
        user_id,
        ex=timedelta(days=app_config.JWT_REFRESH_TOKEN_EXPIRY_DAYS),
    )


async def delete_refresh_token_jti(token_jti: str):
    return await r.delete(f"refresh_token:{token_jti}")


async def set_url_safe_token(prefix: RedisKeysPrefixes, token: str, user_email: str):
    return await r.set(
        name=f"{prefix}:{token}",
        value=user_email,
        ex=timedelta(seconds=app_config.URL_SAFE_TOKEN_MAIL_EXPIRY),
    )


async def get_url_safe_token(prefix: RedisKeysPrefixes, token: str):
    return await r.get(name=f"{prefix}:{token}")


async def delete_url_safe_token(prefix: RedisKeysPrefixes, token: str):
    return await r.delete(f"{prefix}:{token}")
