import os
import time
import requests
import pytest

RUN_INTEGRATION = os.getenv("RUN_INTEGRATION", "0")


@pytest.mark.skipif(RUN_INTEGRATION != "1", reason="Integration tests skipped (set RUN_INTEGRATION=1)")
def test_health_and_incidents_smoke():
    base = "http://127.0.0.1:8000"
    # Wait until health endpoint responds
    for _ in range(20):
        try:
            r = requests.get(f"{base}/api/health", timeout=2)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    r = requests.get(f"{base}/api/health", timeout=2)
    assert r.status_code == 200

    r2 = requests.get(f"{base}/api/incidents/", params={"limit": 1}, timeout=5)
    assert r2.status_code == 200
    data = r2.json()
    assert isinstance(data, list)
