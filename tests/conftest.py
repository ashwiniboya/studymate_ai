"""Pytest configuration and fixtures."""

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["GOOGLE_API_KEY"] = "test-key"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.database.models import Base
from app.database.session import get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    import app.database.session as db_mod

    original_session_local = db_mod.SessionLocal
    db_mod.SessionLocal = TestSession
    yield session
    db_mod.SessionLocal = original_session_local
    session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_txt_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(
            "Photosynthesis is the process by which plants convert light energy into chemical energy. "
            "It occurs in chloroplasts and requires sunlight, water, and carbon dioxide. "
            "The main products are glucose and oxygen. "
            "Chlorophyll is the green pigment that captures light energy."
        )
        path = f.name
    yield path
    Path(path).unlink(missing_ok=True)


@pytest.fixture()
def sample_pdf_content():
    return b"%PDF-1.4 test content"
