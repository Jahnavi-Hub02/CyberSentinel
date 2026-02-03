"""Integration smoke tests (HTTP) for /api/incidents.

These tests are intended to run in CI only. They start against a running
backend (CI job starts uvicorn) and assert authoritative behaviors:
- unspecified `limit` returns the full CSV-derived dataset (no hidden 100 cap)
- `limit=15` returns at most 15 items
- server-side enrichment provides numeric `lat`/`lon` for known locations

Enable locally with: RUN_INTEGRATION=1 python -m pytest -q tests/test_integration_smoke.py
"""
import os
import time
import requests
import pytest

from backend.routers.incidents import load_csv_fallback

BASE = "http://127.0.0.1:8000"

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION", "0") != "1",
    reason="Integration smoke tests are disabled by default (set RUN_INTEGRATION=1)",
)


def _wait_for_health(timeout: int = 20) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if r.ok:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    pytest.fail("backend did not become healthy in time")


def test_incidents_limit_and_enrichment_behavior():
    _wait_for_health()

    # Full dataset (no limit) — authoritative source should return the CSV count
    r_all = requests.get(f"{BASE}/api/incidents/", timeout=10)
    assert r_all.status_code == 200, r_all.text
    all_data = r_all.json()

    expected = load_csv_fallback()
    assert isinstance(all_data, list)
    assert len(all_data) == len(expected), (
        "API /api/incidents/ should return the full CSV fallback when Mongo is absent"
    )

    # Limit behavior — must respect the explicit limit
    r_lim = requests.get(f"{BASE}/api/incidents/?limit=15", timeout=10)
    assert r_lim.status_code == 200, r_lim.text
    lim_data = r_lim.json()

    assert len(lim_data) <= 15
    assert len(lim_data) <= len(all_data)

    # Enrichment: at least one entry in the full response should have numeric lat/lon
    assert any(

    # If the CSV contains known locations, the limited response should include at least
    # one with lat/lon (best-effort — don't fail the whole suite if dataset is tiny)
    if any(e.get("location") for e in expected):
        assert any(
