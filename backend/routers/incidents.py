from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
import uuid
import pandas as pd
from pathlib import Path
from functools import lru_cache

from ..models.incident import Incident, IncidentCreate, serialize_db_incident
from ..db.mongo import incidents_collection


router = APIRouter()


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
            # Use direct indexing for pandas Series instead of .get()
            incident_type = row["Incident_Type"] if "Incident_Type" in row.index else "Unknown"
            city = row["City"] if "City" in row.index else ""
            category = row["Category"] if "Category" in row.index else "Unknown"
            year = int(row["Year"]) if "Year" in row.index and pd.notna(row["Year"]) else 2023
            day = int(row["Day"]) if "Day" in row.index and pd.notna(row["Day"]) else 1
            amount_lost = row["Amount_Lost_INR"] if "Amount_Lost_INR" in row.index else 0

            # Skip clearly invalid rows (no city/location)
            if not city or not str(city).strip():
                continue

            incident = {
                "id": str(uuid.uuid4()),
                "title": f"{incident_type} - {city}",
                "description": f"Incident in {city}",
                "category": category,
                "source": "CSV",
                "timestamp": datetime(year, 1, min(day, 28)),  # Ensure valid day
                "severity": "Medium",
                "location": city,
                "status": "Closed",
                "Incident_Type": incident_type,  # Frontend checks this column name
                "amount_lost": amount_lost,
            }
            incidents.append(incident)
        # Basic de-duplication by (title, timestamp, location)
        seen = set()
        deduped: List[dict] = []
        for inc in incidents:
            key = (inc.get("title"), inc.get("timestamp"), inc.get("location"))
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
    # Return a shallow copy so callers can safely filter without mutating cache
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
        # MongoDB is not available, use CSV fallback
        incidents = load_csv_fallback()
        # Apply filters
        if category:
            incidents = [i for i in incidents if i.get("category") == category]
        if severity:
            incidents = [i for i in incidents if i.get("severity") == severity]
        if location:
            incidents = [i for i in incidents if i.get("location") == location]
        # Sort by timestamp desc and apply limit
        try:
            incidents = sorted(incidents, key=lambda d: d.get("timestamp") or 0, reverse=True)
        except Exception:
            pass
        if limit:
            incidents = incidents[: int(limit)]
        # Server-side geocoding enrichment
        try:
            from ..utils.geocode import enrich_incidents_list
            incidents = enrich_incidents_list(incidents)
        except Exception:
            pass
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
        docs = [serialize_db_incident(d) async for d in cursor]
        # Enrich with lat/lon server-side when possible
        try:
            from ..utils.geocode import enrich_incidents_list
            docs = enrich_incidents_list(docs)
        except Exception:
            pass
        return docs
    except Exception as e:
        # Fallback to CSV
        incidents = load_csv_fallback()
        try:
            incidents = sorted(incidents, key=lambda d: d.get("timestamp") or 0, reverse=True)
        except Exception:
            pass
        # Server-side geocoding enrichment for fallback
        try:
            from ..utils.geocode import enrich_incidents_list
            incidents = enrich_incidents_list(incidents)
        except Exception:
            pass
        return incidents[: (int(limit) if limit else 100)]


@router.post("/", response_model=Incident, status_code=201)
async def create_incident(payload: IncidentCreate) -> Incident:
    """Create a new incident. Requires MongoDB."""
    col = incidents_collection()
    
    if col is None:
        raise HTTPException(status_code=503, detail="Database unavailable. MongoDB is not connected.")
    
    doc = {
        "id": str(uuid.uuid4()),
        "title": payload.title,
        "description": payload.description,
        "category": payload.category,
        "source": payload.source,
        "timestamp": payload.timestamp or datetime.utcnow(),
        "severity": payload.severity,
        "location": payload.location,
        "status": payload.status,
    }
    
    try:
        await col.insert_one(doc)
        return serialize_db_incident(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create incident: {str(e)}")

