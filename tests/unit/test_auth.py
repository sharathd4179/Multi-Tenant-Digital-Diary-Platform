"""
Basic tests for authentication endpoints.

These tests use FastAPI's TestClient to simulate API requests.  They verify
user creation and login flows.  Use `pytest -q` to run.
"""
from uuid import uuid4

from fastapi.testclient import TestClient

from ..main import app


client = TestClient(app)


def test_register_and_login():
    tenant_id = str(uuid4())
    payload = {
        "tenant_id": tenant_id,
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "role": "admin",
    }
    # Register tenant and admin user
    res = client.post("/auth/register-tenant", json=payload)
    assert res.status_code == 201, res.text
    # Login
    login_payload = {
        "tenant_id": tenant_id,
        "username": "testuser",
        "password": "testpassword",
    }
    res2 = client.post("/auth/login", json=login_payload)
    assert res2.status_code == 200
    data = res2.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"