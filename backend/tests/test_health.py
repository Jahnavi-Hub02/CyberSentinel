import os
import requests
from fastapi.testclient import TestClient

from backend.app import app


client = TestClient(app)


def test_health():
    """Health endpoint should respond with status 'online'.

    Prefer a real running server if available (for CI / local runs where
    uvicorn is started separately). If that is unreachable, fall back to
    exercising the FastAPI app via TestClient.
    """
    base = os.getenv("API_BASE", "http://127.0.0.1:8000")

    # Try real HTTP first
    try:
        r = requests.get(f"{base}/health", timeout=2)
        if r.ok:
            data = r.json()
            assert data.get("status") == "online"
            return
    except Exception:
        # Fall back to in-process test client
        pass

    # Test via TestClient if no external server is reachable
    r2 = client.get("/health")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2.get("status") == "online"
