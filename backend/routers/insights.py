"""Insights endpoints for pre-aggregated data used by the frontend maps and charts."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, Request, Response
from collections import Counter
from ..db.mongo import incidents_collection
from ..routers.incidents import load_csv_fallback

import time
import json
import hashlib

router = APIRouter()

# Lightweight city -> lat/lon map (same as frontend list; kept small deliberately)
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


def _city_to_latlon(city: Optional[str]):
    if not city:
        return None, None
    token = str(city).split(",")[0].strip().lower()
    return _CITY_COORDS.get(token, (None, None))


# Simple in-memory cache keyed by (limit,)
_CACHE: dict = {}
_CACHE_TTL = 30  # seconds


def _make_cache_key(limit: int, min_count: int):
    return (int(limit), int(min_count))


def _fetch_top_from_csv(limit: int) -> List[Dict[str, Any]]:
    incidents = load_csv_fallback()
    counts = Counter()
    for i in incidents:
        loc = i.get("location") or i.get("City") or ""
        if loc:
            counts[str(loc).strip()] += 1
    items = counts.most_common(limit)
    out = []
    for loc, cnt in items:
        lat, lon = _city_to_latlon(loc)
        out.append({"location": loc, "count": cnt, "lat": lat, "lon": lon})
    return out


async def _fetch_top_from_mongo(limit: int) -> List[Dict[str, Any]]:
    col = incidents_collection()
    results = []
    try:
        pipeline = [
            {"$group": {"_id": {"location": "$location"}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        cursor = col.aggregate(pipeline)
        async for doc in cursor:
            loc = doc.get("_id", {}).get("location") or ""
            cnt = int(doc.get("count", 0))
            lat, lon = _city_to_latlon(loc)
            results.append({"location": loc, "count": cnt, "lat": lat, "lon": lon})
        return results
    except Exception:
        # if anything goes wrong, fallback to CSV
        return _fetch_top_from_csv(limit)


@router.get("/insights/top-locations")
async def top_locations(request: Request, limit: int = Query(10, ge=1, le=200), min_count: int = Query(0, ge=0)) -> Response:
    """Return top locations by incident count.

    Supports optional `min_count` to filter low-frequency locations. Uses caching (ttl) and returns ETag header for client-side caching (304 responses).
    """
    key = _make_cache_key(limit, min_count)
    now = time.time()

    # Return cached if fresh
    cached = _CACHE.get(key)
    if cached:
        data, ts, etag = cached
        if now - ts <= _CACHE_TTL:
            # honor If-None-Match
            inm = request.headers.get("if-none-match")
            if inm and inm == etag:
                return Response(status_code=304)
            return Response(content=json.dumps(data), media_type="application/json", headers={"ETag": etag})

    col = incidents_collection()
    if col is None:
        data = _fetch_top_from_csv(limit)
    else:
        data = await _fetch_top_from_mongo(limit)

    # apply min_count filter and trimming
    if min_count > 0:
        data = [d for d in data if int(d.get("count", 0)) >= min_count]

    # compute etag
    etag = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    # cache the result
    _CACHE[key] = (data, now, etag)

    # honor If-None-Match
    inm = request.headers.get("if-none-match")
    if inm and inm == etag:
        return Response(status_code=304)

    return Response(content=json.dumps(data), media_type="application/json", headers={"ETag": etag})
