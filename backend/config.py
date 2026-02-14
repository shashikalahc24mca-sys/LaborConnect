from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Default CORS origins for dev (when allow_credentials=True, browser forbids "*")
_DEFAULT_CORS_ORIGINS = [
    "http://localhost:8081",
    "http://localhost:19006",
    "http://localhost:3000",
    "http://127.0.0.1:8081",
    "http://127.0.0.1:3000",
]


class Settings(BaseModel):
    firebase_credentials_path: Path
    firebase_db_url: str
    api_host: str = "0.0.0.0"
    api_port: int = 8010  # avoid reserved/conflicting ports on Windows
    cors_origins: list[str] = _DEFAULT_CORS_ORIGINS.copy()


def load_settings() -> Settings:
    # Load environment variables from a .env file at project root
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "").strip()
    db_url = os.getenv("FIREBASE_DB_URL", "").strip()

    if not creds_path or not db_url:
        raise RuntimeError(
            "FIREBASE_CREDENTIALS_PATH and FIREBASE_DB_URL must be set in environment "
            "or .env file at project root."
        )

    cors_raw = os.getenv("CORS_ORIGINS", "").strip()
    if cors_raw:
        origins = [o.strip() for o in cors_raw.split(",") if o.strip()]
    else:
        origins = _DEFAULT_CORS_ORIGINS.copy()

    return Settings(
        firebase_credentials_path=Path(creds_path),
        firebase_db_url=db_url,
        cors_origins=origins,
    )


settings = load_settings()
