import requests
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

BASE_URL = "https://api.jayaraj.dev:8443"

# Path to your trusted certificate
CERT_PATH = Path(__file__).parent / "cert.crt"


def pretty(data):
    print(json.dumps(data, indent=2, default=str))


def request(method, path, **kwargs):
    """
    Centralized request wrapper with TLS verification
    """
    url = f"{BASE_URL}{path}"
    return requests.request(
        method,
        url,
        verify=str(CERT_PATH),
        timeout=10,
        **kwargs
    )


# ------------------------------------------------------------
# HEALTH
# ------------------------------------------------------------

def test_health():
    print("\n=== GET /health ===")
    resp = request("GET", "/health")
    print(f"Status: {resp.status_code}")
    pretty(resp.json())


# ------------------------------------------------------------
# EVENTS
# ------------------------------------------------------------

def test_publish_event():
    print("\n=== POST /api/v1/events/ ===")

    payload = {
        "type": "user.signup",
        "payload": {
            "user_id": 123,
            "info": "Test user"
        }
    }

    resp = request("POST", "/api/v1/events/", json=payload)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    pretty(data)
    return data.get("id")


def test_list_events():
    print("\n=== GET /api/v1/events/ ===")
    resp = request("GET", "/api/v1/events/?limit=10")
    print(f"Status: {resp.status_code}")
    pretty(resp.json())


# ------------------------------------------------------------
# NOTIFICATIONS
# ------------------------------------------------------------

def test_create_notification():
    print("\n=== POST /api/v1/notifications/ ===")

    payload = {
        "notification_type": "user.signup",
        "entity_id": "user-123",
        "target_date": (
            datetime.now(timezone.utc) + timedelta(days=10)
        ).isoformat(),
        "lead_time_days": 7,
        "email": "user@example.com",
        "phone": "9999912345"
    }

    resp = request("POST", "/api/v1/notifications/", json=payload)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    pretty(data)
    return data.get("id")


def test_delete_notification(notification_id):
    print("\n=== DELETE /api/v1/notifications/{id} ===")
    resp = request("DELETE", f"/api/v1/notifications/{notification_id}")
    print(f"Status: {resp.status_code}")
    pretty(resp.json())


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def run_all():
    print("======================================")
    print(" DEPLOYED EVENT SYSTEM API TEST")
    print("======================================")

    test_health()

    event_id = test_publish_event()
    test_list_events()

    notif_id = test_create_notification()
    if notif_id:
        test_delete_notification(notif_id)


if __name__ == "__main__":
    run_all()
