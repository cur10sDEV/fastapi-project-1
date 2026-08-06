from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    JWT_SECRET: str = Field(min_length=64, max_length=1024)
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRY_SECONDS: int
    JWT_REFRESH_TOKEN_EXPIRY_DAYS: int
    REDIS_HOST: str
    REDIS_PORT: str


app_config = Settings()
