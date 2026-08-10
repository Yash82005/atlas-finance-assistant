from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    GEMINI_API_KEY: str
    DATABASE_URL: str
    NEWS_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()