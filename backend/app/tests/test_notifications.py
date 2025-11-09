def test_create_reminder_api():
    # Use TestClient to call endpoints
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    payload = {
        "target_type": "password_expiry",
        "target_identifier": "user123",
        "target_date": "2030-01-01T00:00:00Z",
        "lead_time_days": 7,
        "contact_email": "test@example.com"
    }
    r = client.post("/api/v1/notifications/reminders", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["target_type"] == "password_expiry"
