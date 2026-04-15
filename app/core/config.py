import os
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL

class Settings(BaseSettings):
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5433))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "depfund")
    LOG_SQL_QUERIES: bool = os.getenv("LOG_SQL_QUERIES", "0") == "1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")

    @property
    def DATABASE_URL(self) -> str:
        return URL.create(
            "postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)


settings = Settings()