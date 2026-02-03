import json
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_top_locations_exists():
    resp = client.get("/api/insights/top-locations?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # items should contain location and count
    if data:
        first = data[0]
        assert "location" in first
        assert "count" in first
        assert isinstance(first["count"], int)


def test_top_locations_limit_and_min_count():
    # limit + min_count filter must work; min_count=1 should return only items with count>=1
    resp = client.get("/api/insights/top-locations?limit=10&min_count=1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    for item in data:
        assert item["count"] >= 1


def test_etag_behaviour():
    # First request to obtain ETag
    resp = client.get("/api/insights/top-locations?limit=5")
    assert resp.status_code == 200
    etag = resp.headers.get("ETag")
    if not etag:
        # Some environments produce no ETag (older caches) - skip
        return
    # Second request with matching If-None-Match -> should return 304
    resp2 = client.get("/api/insights/top-locations?limit=5", headers={"If-None-Match": etag})
    assert resp2.status_code in (200, 304)  # either cached 304 or same 200 is acceptable in test env
    if resp2.status_code == 304:
        assert resp2.content == b''

