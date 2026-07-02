"""Application configuration."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # AI
    google_api_key: str = ""
    model_name: str = "gemini-2.5-flash"

    # Database — set POSTGRES_URL in Vercel env vars (from Vercel Postgres / Neon / Supabase)
    postgres_url: str = ""
    database_url: str = "sqlite:///./data/studymate.db"  # local fallback only

    # Chroma Cloud — set these in Vercel env vars
    chroma_api_key: str = ""
    chroma_tenant: str = ""
    chroma_database: str = ""

    # Local-only fallback paths (not used on Vercel)
    chroma_persist_dir: str = "./data/chroma"
    upload_dir: str = "./data/uploads"

    # RAG settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "models/text-embedding-004"  # Gemini embedding model

    @property
    def is_vercel(self) -> bool:
        return os.getenv("VERCEL", "") == "1"

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def data_dir(self) -> Path:
        if self.is_vercel:
            return Path("/tmp/studymate_data")
        return self.base_dir / "data"

    @property
    def upload_path(self) -> Path:
        configured = Path(self.upload_dir)
        if self.is_vercel and not str(configured).startswith("/tmp"):
            return self.data_dir / "uploads"
        return configured

    @property
    def chroma_path(self) -> Path:
        return self.data_dir / "chroma"

    @property
    def runtime_database_url(self) -> str:
        """Return Postgres URL on Vercel, SQLite locally."""
        if self.postgres_url:
            return self.postgres_url
        if self.is_vercel:
            # Vercel without POSTGRES_URL set — warn loudly
            raise RuntimeError(
                "POSTGRES_URL environment variable is not set. "
                "Create a Postgres database in Vercel dashboard → Storage and link it to this project."
            )
        return self.database_url

    @property
    def use_chroma_cloud(self) -> bool:
        """True when Chroma Cloud credentials are available."""
        return bool(self.chroma_api_key and self.chroma_tenant and self.chroma_database)


settings = Settings()


def ensure_directories() -> None:
    """Create required data directories on startup (local dev only)."""
    if not settings.is_vercel:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        settings.upload_path.mkdir(parents=True, exist_ok=True)
        settings.chroma_path.mkdir(parents=True, exist_ok=True)
    else:
        # On Vercel only create the upload dir in /tmp (read-only uploads are ephemeral anyway)
        settings.upload_path.mkdir(parents=True, exist_ok=True)
