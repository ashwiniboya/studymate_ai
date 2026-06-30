"""Application configuration."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    google_api_key: str = ""
    database_url: str = "sqlite:///./data/studymate.db"
    chroma_persist_dir: str = "./data/chroma"
    upload_dir: str = "./data/uploads"
    model_name: str = "gemini-2.5-flash"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "all-MiniLM-L6-v2"

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
        configured = Path(self.chroma_persist_dir)
        if self.is_vercel and not str(configured).startswith("/tmp"):
            return self.data_dir / "chroma"
        return configured

    @property
    def runtime_database_url(self) -> str:
        if self.is_vercel and self.database_url.startswith("sqlite:///./"):
            return "sqlite:////tmp/studymate_data/studymate.db"
        return self.database_url


settings = Settings()


def ensure_directories() -> None:
    """Create required data directories on startup."""
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
