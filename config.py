from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_", env_file="src/.env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str


config = Settings()
