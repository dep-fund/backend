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
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v3/userinfo"
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Estos se leen desde secrets, con fallback a env vars para desarrollo local
    POSTGRES_USER: str = _read_secret("postgres_user", os.getenv("POSTGRES_USER", "postgres"))
    POSTGRES_PASSWORD: str = _read_secret("postgres_password", os.getenv("POSTGRES_PASSWORD", "postgres"))
    POSTGRES_DB: str = _read_secret("postgres_db", os.getenv("POSTGRES_DB", "depfund"))
    SECRET_KEY: str = _read_secret("secret_key", os.getenv("SECRET_KEY", ""))
    ADMIN_SECRET_KEY: str = _read_secret("admin_secret_key", os.getenv("ADMIN_SECRET_KEY", "develop"))
    GOOGLE_CLIENT_ID: str = _read_secret("google_client_id", os.getenv("GOOGLE_CLIENT_ID", "develop"))
    GOOGLE_CLIENT_SECRET: str = _read_secret("google_client_secret", os.getenv("GOOGLE_CLIENT_SECRET", "develop"))
    GOOGLE_REDIRECT_URI: str = _read_secret("google_redirect_uri", os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"))

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