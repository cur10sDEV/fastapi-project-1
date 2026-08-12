from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_SALT: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRY_SECONDS: int
    JWT_REFRESH_TOKEN_EXPIRY_DAYS: int
    URL_SAFE_TOKEN_SECRET: str
    URL_SAFE_TOKEN_SALT: str
    URL_SAFE_TOKEN_MAIL_EXPIRY: int = 3600  # seconds - 1 hour
    REDIS_HOST: str
    REDIS_PORT: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str
    NAME: str = "FastAPI Start"


app_config = Settings()

# will be read by celery
broker_url = f"redis://{app_config.REDIS_HOST}:{app_config.REDIS_PORT}/0"
result_backend = f"redis://{app_config.REDIS_HOST}:{app_config.REDIS_PORT}/0"
broker_connection_retry_on_startup = True
