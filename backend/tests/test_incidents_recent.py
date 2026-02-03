from fastapi.testclient import TestClient
from backend.app import app


def test_incidents_limit_fallback():
    client = TestClient(app)
    r = client.get("/api/incidents/?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Should be at most 5 items
    assert len(data) <= 5
    # If any returned, they should have an ISO timestamp string
    if data:
        assert "timestamp" in data[0]
        assert isinstance(data[0]["timestamp"], str)
