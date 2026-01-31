"""Simple server-side geocoding with optional persistent cache.

This module maps a small set of Indian city names to lat/lon and maintains a
small disk-backed cache under `data/geocode_cache.json` so results persist
between runs. It is intentionally lightweight and deterministic (no external
API calls) so it is safe for offline CI and demo usage.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Tuple, Optional, Dict

# Minimal curated mapping (same as frontend)
_CITY_COORDS = {
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "kolkata": (22.5726, 88.3639),
    "chennai": (13.0827, 80.2707),
    "lucknow": (26.8467, 80.9462),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "surat": (21.1702, 72.8311),
    "noida": (28.5355, 77.3910),
    "gurugram": (28.4595, 77.0266),
    "gurgaon": (28.4595, 77.0266),
    "coimbatore": (11.0168, 76.9558),
    "kochi": (9.9312, 76.2673),
}

_CACHE: Dict[str, Tuple[float, float]] = {}
_CACHE_FILE = Path(__file__).resolve().parents[1] / "data" / "geocode_cache.json"


def _load_cache() -> None:
    global _CACHE
    try:
        if _CACHE_FILE.exists():
            with _CACHE_FILE.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
                _CACHE = {k: tuple(v) for k, v in data.items()}
    except Exception:
        _CACHE = {}


def _save_cache() -> None:
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _CACHE_FILE.open("w", encoding="utf-8") as fh:
            json.dump({k: list(v) for k, v in _CACHE.items()}, fh)
    except Exception:
        pass


def _normalize_location(loc: Optional[str]) -> Optional[str]:
    if not loc:
        return None
    return str(loc).split(",")[0].strip().lower()


def geocode_location(loc: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    """Return (lat, lon) for a location name if known, else (None, None)."""
    if loc is None:
        return None, None
    norm = _normalize_location(loc)
    if not norm:
        return None, None
    # load cache lazily
    if not _CACHE:
        _load_cache()
    if norm in _CACHE:
        lat, lon = _CACHE[norm]
        return float(lat), float(lon)
    # check curated city map
    if norm in _CITY_COORDS:
        lat, lon = _CITY_COORDS[norm]
        _CACHE[norm] = (lat, lon)
        _save_cache()
        return float(lat), float(lon)
    return None, None


def enrich_incident(inc: Dict) -> Dict:
    """Ensure incident dict has `lat` and `lon` keys when possible."""
    if not isinstance(inc, dict):
        return inc
    if "lat" in inc and "lon" in inc and inc.get("lat") is not None and inc.get("lon") is not None:
        return inc
    lat, lon = geocode_location(inc.get("location"))
    if lat is not None and lon is not None:
        inc["lat"] = lat
        inc["lon"] = lon
    return inc


def enrich_incidents_list(incidents: list) -> list:
    for i in incidents:
        try:
            enrich_incident(i)
        except Exception:
            continue
    return incidents
