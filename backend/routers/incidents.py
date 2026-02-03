from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timezone
import uuid
import pandas as pd
from pathlib import Path
from functools import lru_cache

from ..models.incident import Incident, IncidentCreate
from ..db.mongo import incidents_collection
from ..utils.geocode import geocode_location


router = APIRouter()


def _format_timestamp(value: Any) -> str:
    """Normalize timestamps to ISO-8601 UTC strings."""
    if value is None or value == "":
        dt = datetime.now(timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")
    if isinstance(value, datetime):
        dt = value
    elif hasattr(value, "to_pydatetime"):
        dt = value.to_pydatetime()
    else:
        try:
            dt = pd.to_datetime(value, errors="coerce").to_pydatetime()
        except Exception:
            dt = None
    if dt is None:
        dt = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def _normalize_incident_id(value: Optional[str]) -> str:
    """Ensure every incident id is in the INC-xxxx format."""
    if value is None or str(value).strip() == "":
        return f"INC-{uuid.uuid4().hex[:8].upper()}"
    raw = str(value).strip()
    if raw.startswith("INC-"):
        return raw
    if raw.isdigit():
        return f"INC-{raw}"
    return f"INC-{raw}"


def _standardize_incident(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Convert raw incident data into the standard response schema."""
    location = raw.get("location") or raw.get("City") or raw.get("city") or ""
    incident_type = (
        raw.get("type")
        or raw.get("incident_type")
        or raw.get("Incident_Type")
        or raw.get("title")
        or "Unknown"
    )
    category = raw.get("category") or raw.get("Category") or "Unknown"
    severity = raw.get("severity") or raw.get("Severity") or "Medium"
    lat = raw.get("latitude") if raw.get("latitude") is not None else raw.get("lat")
    lon = raw.get("longitude") if raw.get("longitude") is not None else raw.get("lon")
    if lat is None or lon is None:
        geo_lat, geo_lon = geocode_location(location)
        lat = lat if lat is not None else geo_lat
        lon = lon if lon is not None else geo_lon

    standard = {
        "id": _normalize_incident_id(raw.get("id") or raw.get("incident_id") or raw.get("uid")),
        "type": str(incident_type),
        "category": str(category),
        "severity": str(severity),
        "latitude": float(lat) if lat is not None else None,
        "longitude": float(lon) if lon is not None else None,
        "location": str(location),
        "timestamp": _format_timestamp(raw.get("timestamp") or raw.get("date") or raw.get("Timestamp")),
    }

    for key in ("title", "description", "status", "source", "amount_lost", "Incident_Type", "incident_type"):
        if key in raw:
            standard[key] = raw[key]
    return standard


def _timestamp_sort_key(incident: Dict[str, Any]) -> datetime:
    """Parse standardized incident timestamps for sorting."""
    ts = incident.get("timestamp")
    try:
        return pd.to_datetime(ts, errors="coerce").to_pydatetime() or datetime.min.replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


@lru_cache(maxsize=1)
def _load_csv_fallback_cached() -> List[dict]:
    """Load incidents from CSV as fallback when MongoDB is unavailable.

    Cached in-memory so repeated `/api/incidents/` calls do not re-read the CSV
    on every request. This keeps behavior identical while avoiding heavy work
    on the hot path.
    """
    project_root = Path(__file__).parent.parent.parent
    csv_path = project_root / "backend" / "data" / "cybersecurity_cases_india_combined.csv"

    if not csv_path.exists():
        return []

    try:
        df = pd.read_csv(csv_path, low_memory=False)
        incidents: List[dict] = []
        for _, row in df.iterrows():
            incident_type = row["Incident_Type"] if "Incident_Type" in row.index else "Unknown"
            city = row["City"] if "City" in row.index else ""
            category = row["Category"] if "Category" in row.index else "Unknown"
            year = int(row["Year"]) if "Year" in row.index and pd.notna(row["Year"]) else 2023
            day = int(row["Day"]) if "Day" in row.index and pd.notna(row["Day"]) else 1
            amount_lost = row["Amount_Lost_INR"] if "Amount_Lost_INR" in row.index else 0

            if not city or not str(city).strip():
                continue

            raw_incident = {
                "id": str(uuid.uuid4()),
                "title": f"{incident_type} - {city}",
                "description": f"Incident in {city}",
                "category": category,
                "source": "CSV",
                "timestamp": datetime(year, 1, min(day, 28)),
                "severity": "Medium",
                "location": city,
                "status": "Closed",
                "Incident_Type": incident_type,
                "amount_lost": amount_lost,
            }
            incidents.append(_standardize_incident(raw_incident))

        seen = set()
        deduped: List[dict] = []
        for inc in incidents:
            key = (inc.get("type"), inc.get("timestamp"), inc.get("location"))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(inc)
        return deduped
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []


def load_csv_fallback() -> List[dict]:
    """Public wrapper around cached CSV load."""
    return list(_load_csv_fallback_cached())


@router.get("/", response_model=List[Incident])
async def list_incidents(
    category: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    location: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: Optional[int] = Query(default=None, ge=1, le=200),
):
    """Get incidents with optional filtering. Uses MongoDB if available, otherwise CSV.

    Supports `limit` to return only the most recent N incidents (sorted by timestamp desc).
    """
    col = incidents_collection()
    
    if col is None:
        incidents = load_csv_fallback()
        if category:
            incidents = [i for i in incidents if i.get("category") == category]
        if severity:
            incidents = [i for i in incidents if i.get("severity") == severity]
        if source:
            incidents = [i for i in incidents if i.get("source") == source]
        if location:
            incidents = [i for i in incidents if i.get("location") == location]
        if status:
            incidents = [i for i in incidents if i.get("status") == status]
        incidents = sorted(incidents, key=_timestamp_sort_key, reverse=True)
        if limit:
            incidents = incidents[: int(limit)]
        return incidents
    
    # Use MongoDB
    filters = {}
    if category:
        filters["category"] = category
    if severity:
        filters["severity"] = severity
    if source:
        filters["source"] = source
    if location:
        filters["location"] = location
    if status:
        filters["status"] = status

    try:
        cursor = col.find(filters).sort("timestamp", -1)
        if limit:
            cursor = cursor.limit(limit)
        docs = [_standardize_incident(d) async for d in cursor]
        return docs
    except Exception as e:
        # Fallback to CSV
        incidents = load_csv_fallback()
        incidents = sorted(incidents, key=_timestamp_sort_key, reverse=True)
        return incidents[: (int(limit) if limit else 100)]


@router.post("/", response_model=Incident, status_code=201)
async def create_incident(payload: IncidentCreate) -> Incident:
    """Create a new incident. Requires MongoDB."""
    col = incidents_collection()
    
    if col is None:
        raise HTTPException(status_code=503, detail="Database unavailable. MongoDB is not connected.")
    
    parsed_timestamp = pd.to_datetime(payload.timestamp, errors="coerce") if payload.timestamp else None
    if parsed_timestamp is not None and not pd.isna(parsed_timestamp):
        timestamp_value = parsed_timestamp.to_pydatetime()
    else:
        timestamp_value = datetime.now(timezone.utc)

    doc = {
        "id": _normalize_incident_id(None),
        "type": payload.type,
        "category": payload.category,
        "severity": payload.severity,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "location": payload.location,
        "timestamp": timestamp_value,
        "status": "Active",
        "source": "API",
    }
    
    try:
        await col.insert_one(doc)
        return _standardize_incident(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create incident: {str(e)}")
