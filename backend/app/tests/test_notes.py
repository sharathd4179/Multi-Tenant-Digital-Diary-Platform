"""
Tests for note endpoints.
"""
from uuid import uuid4

from fastapi.testclient import TestClient

from ..main import app


client = TestClient(app)


def setup_user_and_token():
    tenant_id = str(uuid4())
    # Register tenant and admin user
    payload = {
        "tenant_id": tenant_id,
        "username": "tester",
        "email": "tester@example.com",
        "password": "password",
        "role": "admin",
    }
    client.post("/auth/register-tenant", json=payload)
    # Login
    login_payload = {
        "tenant_id": tenant_id,
        "username": "tester",
        "password": "password",
    }
    res = client.post("/auth/login", json=login_payload)
    token = res.json()["access_token"]
    return tenant_id, token


def test_create_note():
    tenant_id, token = setup_user_and_token()
    # Decode user id from token
    import base64, json
    payload_json = base64.urlsafe_b64decode(token.split(".")[1] + "==").decode()
    payload = json.loads(payload_json)
    user_id = payload.get("sub")
    # Create note
    note_payload = {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "title": "Test Note",
        "content": "This is a test note.",
        "tags": ["test"],
    }
    res = client.post("/notes/", json=note_payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201, res.text
    note = res.json()
    assert note["title"] == "Test Note"
    # List notes
    res2 = client.get("/notes/", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 200
    notes = res2.json()
    assert len(notes) >= 1