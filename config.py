from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    ADMIN_ID: int = 0
    DATABASE_PATH: str = "quiz_bot.db"
    ALLOWED_USERS_FILE: str = "allowed_users.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
