from datetime import timedelta

from redis.asyncio import Redis

from src.config import app_config

r = Redis(
    host=app_config.REDIS_HOST,
    port=app_config.REDIS_PORT,
    decode_responses=True,
)


async def get_redis():
    return await r


async def check_refresh_token_jti(token_jti: str, user_id: str):
    stored_user_id = await r.get(f"refresh_token:{token_jti}")
    return stored_user_id == user_id


async def set_refresh_token_jti(token_jti: str, user_id: str):
    return await r.set(
        f"refresh_token:{token_jti}",
        user_id,
        ex=timedelta(days=app_config.JWT_REFRESH_TOKEN_EXPIRY_DAYS),
    )


async def delete_refresh_token_jti(token_jti: str):
    return await r.delete(f"refresh_token:{token_jti}")
