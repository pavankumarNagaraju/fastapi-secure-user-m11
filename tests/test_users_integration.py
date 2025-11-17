import uuid

from fastapi.testclient import TestClient


def test_create_user_success(client: TestClient):
    unique_suffix = uuid.uuid4().hex[:6]
    payload = {
        "username": f"pavan_{unique_suffix}",
        "email": f"pavan_{unique_suffix}@example.com",
        "password": "secret123",
    }

    response = client.post("/users/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "created_at" in data
    # Password must not be in response
    assert "password_hash" not in data
    assert "password" not in data


def test_create_user_duplicate_username_or_email(client: TestClient):
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"pavan_duplicate_{unique_suffix}"
    email = f"pavan_duplicate_{unique_suffix}@example.com"

    payload1 = {"username": username, "email": email, "password": "secret123"}
    payload2 = {"username": username, "email": email, "password": "anotherpass"}

    # First creation should succeed
    resp1 = client.post("/users/", json=payload1)
    assert resp1.status_code == 201

    # Second creation with same username/email should fail
    resp2 = client.post("/users/", json=payload2)
    assert resp2.status_code == 400
    assert "Username or email already exists" in resp2.json()["detail"]


def test_create_user_invalid_email_returns_422(client: TestClient):
    payload = {
        "username": "pavan_bad_email_user",
        "email": "not-an-email",
        "password": "secret123",
    }

    response = client.post("/users/", json=payload)
    # FastAPI/Pydantic validation error
    assert response.status_code == 422
