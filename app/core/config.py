import os
from pathlib import Path
import cloudinary
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
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "depfund.soporte@gmail.com")
    SENDER_PASSWORD: str = _read_secret(
        "sender_password", os.getenv("SENDER_PASSWORD", "")
    )
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://depfund.vercel.app")
    BACKOFFICE_URL: str = os.getenv(
        "BACKOFFICE_URL", "https://depfund-admin.vercel.app"
    )

    RPC_URL: str = os.getenv("RPC_URL", "http://127.0.0.1:8545")
    BLOCKCHAIN_ARTIFACTS_PATH: str = os.getenv(
        "BLOCKCHAIN_ARTIFACTS_PATH", "/blockchain/out"
    )
    TREASURY_ADDRESS: str = os.getenv(
        "TREASURY_ADDRESS", "0x2560d5b0CDe93D618425FadfC9F5511e8730Af90"
    )
    USDC_ADDRESS: str = os.getenv(
        "USDC_ADDRESS", "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
    )
    MARKETPLACE_ADDRESS: str = os.getenv(
        "MARKETPLACE_ADDRESS", "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"
    )
    FACTORY_ADDRESS: str = os.getenv(
        "FACTORY_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    )
    PLATFORM_ADDRESS: str = os.getenv(
        "PLATFORM_ADDRESS", "0x2560d5b0CDe93D618425FadfC9F5511e8730Af90"
    )

    POSTGRES_USER: str = _read_secret(
        "postgres_user", os.getenv("POSTGRES_USER", "postgres")
    )
    POSTGRES_PASSWORD: str = _read_secret(
        "postgres_password", os.getenv("POSTGRES_PASSWORD", "postgres")
    )
    POSTGRES_DB: str = _read_secret("postgres_db", os.getenv("POSTGRES_DB", "depfund"))
    SECRET_KEY: str = _read_secret("secret_key", os.getenv("SECRET_KEY", ""))
    ADMIN_SECRET_KEY: str = _read_secret(
        "admin_secret_key", os.getenv("ADMIN_SECRET_KEY", "develop")
    )
    GOOGLE_CLIENT_ID: str = _read_secret(
        "google_client_id", os.getenv("GOOGLE_CLIENT_ID", "develop")
    )
    GOOGLE_CLIENT_SECRET: str = _read_secret(
        "google_client_secret", os.getenv("GOOGLE_CLIENT_SECRET", "develop")
    )
    GOOGLE_REDIRECT_URI: str = _read_secret(
        "google_redirect_uri",
        os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"),
    )
    CLOUDINARY_CLOUD_NAME: str = _read_secret(
        "cloudinary_cloud_name", os.getenv("CLOUDINARY_CLOUD_NAME", "")
    )
    CLOUDINARY_API_KEY: str = _read_secret(
        "cloudinary_api_key", os.getenv("CLOUDINARY_API_KEY", "")
    )
    CLOUDINARY_API_SECRET: str = _read_secret(
        "cloudinary_api_secret", os.getenv("CLOUDINARY_API_SECRET", "")
    )
    DEPLOYER_PRIVATE_KEY: str = _read_secret(
        "deployer_private_key", os.getenv("DEPLOYER_PRIVATE_KEY", "")
    )

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

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)
