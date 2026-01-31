import requests
from fastapi.testclient import TestClient


def test_health():
    # Prefer real server if running, otherwise fall back to TestClient(app)
    try:
        r = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
        assert r.status_code == 200
        assert r.json().get("status") == "ok"
    except requests.exceptions.RequestException:
        # Try in-process app
        from backend.app import app
        client = TestClient(app)
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"