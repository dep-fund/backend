import os
from pathlib import Path
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL


def _read_secret(name: str, fallback: str = "") -> str:
    """Lee un Docker Secret desde /run/secrets/, con fallback para desarrollo local."""
    secret_path = Path(f"/run/secrets/{name}")
    if secret_path.exists():
        return secret_path.read_text().strip()
    return fallback


class Settings(BaseSettings):
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5433))
    LOG_SQL_QUERIES: bool = os.getenv("LOG_SQL_QUERIES", "0") == "1"

    POSTGRES_USER: str = _read_secret("postgres_user", os.getenv("POSTGRES_USER", "postgres"))
    POSTGRES_PASSWORD: str = _read_secret("postgres_password", os.getenv("POSTGRES_PASSWORD", "postgres"))
    POSTGRES_DB: str = _read_secret("postgres_db", os.getenv("POSTGRES_DB", "depfund"))
    SECRET_KEY: str = _read_secret("secret_key", os.getenv("SECRET_KEY", ""))
    ADMIN_SECRET_KEY: str = _read_secret("admin_secret_key", os.getenv("ADMIN_SECRET_KEY", "develop"))

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "depfund.soporte@gmail.com")
    SENDER_PASSWORD: str = _read_secret("sender_password", os.getenv("SENDER_PASSWORD", ""))

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    BACKOFFICE_URL: str = os.getenv("BACKOFFICE_URL", "http://localhost:5174")

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