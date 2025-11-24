import requests
from datetime import datetime, timedelta, timezone
import json

BASE_URL = "http://localhost:5001"   # change if using ngrok/k8s ingress


def pretty(data):
    print(json.dumps(data, indent=2, default=str))


def test_health():
    print("\n=== /health ===")
    url = f"{BASE_URL}/health"
    resp = requests.get(url)
    print(f"Status: {resp.status_code}")
    try:
        pretty(resp.json())
    except:
        print(resp.text)


# ------------------------------------------------------------
# EVENTS
# ------------------------------------------------------------

def test_publish_event():
    print("\n=== POST /api/v1/events/ (Publish Event) ===")
    url = f"{BASE_URL}/api/v1/events/"

    payload = {
        "type": "user.signup",
        "payload": {
            "user_id": 123,
            "info": "Test user"
        }
    }

    resp = requests.post(url, json=payload)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    pretty(data)
    return data.get("id")


def test_list_events():
    print("\n=== GET /api/v1/events/ (List Events) ===")
    url = f"{BASE_URL}/api/v1/events/?limit=10"
    resp = requests.get(url)
    print(f"Status: {resp.status_code}")
    pretty(resp.json())


# ------------------------------------------------------------
# NOTIFICATIONS
# ------------------------------------------------------------

def test_create_notification():
    print("\n=== POST /api/v1/notifications/ (Create Notification) ===")
    url = f"{BASE_URL}/api/v1/notifications/"

    payload = {
        "notification_type": "user.signup",
        "entity_id": "user-123",
        "target_date": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
        "lead_time_days": 7,
        "email": "user@example.com",
        "phone": "9999912345"
    }

    resp = requests.post(url, json=payload)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    pretty(data)
    return data.get("id")


def test_delete_notification(notification_id: int):
    print("\n=== DELETE /api/v1/notifications/{id} (Cancel Notification) ===")
    url = f"{BASE_URL}/api/v1/notifications/{notification_id}"
    resp = requests.delete(url)
    print(f"Status: {resp.status_code}")
    pretty(resp.json())


# ------------------------------------------------------------
# MAIN RUNNER
# ------------------------------------------------------------

def run_all():
    print("======================================")
    print("     EVENT & NOTIFICATION TESTER")
    print("======================================")

    # Health check
    test_health()

    # Event Endpoints
    event_id = test_publish_event()
    test_list_events()

    # Notification Endpoints
    notif_id = test_create_notification()

    if notif_id:
        test_delete_notification(notif_id)
    else:
        print("Notification was not created, delete test skipped.")


if __name__ == "__main__":
    run_all()
