import requests
from fastapi.testclient import TestClient


def test_health():
    # Prefer real server if running, otherwise fall back to TestClient(app)
    try:

    except requests.exceptions.RequestException:
        # Try in-process app
        from backend.app import app
        client = TestClient(app)
