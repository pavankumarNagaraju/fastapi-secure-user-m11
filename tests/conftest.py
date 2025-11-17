import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal, get_db


# Ensure tables exist for tests
@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally drop tables after tests:
    # Base.metadata.drop_all(bind=engine)


# Override the get_db dependency to use our SessionLocal
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)
