"""Pytest fixtures for backend testing."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.services.auth_service import AuthService

# Use an in-memory SQLite database specifically for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh tables for each test and tear down cleanly after."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    # Seed default admin for tests
    AuthService.seed_initial_admin(session)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
