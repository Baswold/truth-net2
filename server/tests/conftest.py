from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Set environment variables before importing app modules
os.environ.setdefault("TRUTHNET_JWT_SECRET", "test-secret-key-that-is-long-enough-1234567890")
os.environ.setdefault("TRUTHNET_DATABASE_URL", "sqlite:///test.db")

from app.database import Base, get_session
from app.main import create_app
import app.models  # noqa: F401 - ensure model metadata is loaded

TEST_DB_PATH = Path("test.db")


@pytest.fixture(scope="session")
def engine() -> Generator:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    engine = create_engine(
        f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()


@pytest.fixture()
def client_and_session(engine) -> Generator[tuple[TestClient, Session], None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    TestingSession = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = TestingSession()

    app = create_app()

    def override_get_session():
        try:
            yield session
        finally:
            session.expire_all()

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)

    try:
        yield client, session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def session(client_and_session) -> Session:
    _, session = client_and_session
    return session


@pytest.fixture()
def client(client_and_session) -> TestClient:
    client, _ = client_and_session
    return client
