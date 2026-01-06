from typing import List, Optional
from fastapi import APIRouter, Query
from datetime import datetime
import uuid

from models.incident import Incident, IncidentCreate, serialize_db_incident
from db.mongo import incidents_collection


router = APIRouter()


@router.get("/", response_model=List[Incident])
async def list_incidents(
    category: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    location: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
):
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

    cursor = incidents_collection().find(filters).sort("timestamp", -1)
    docs = [serialize_db_incident(d) async for d in cursor]
    return docs


@router.post("/", response_model=Incident, status_code=201)
async def create_incident(payload: IncidentCreate) -> Incident:
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
    await incidents_collection().insert_one(doc)
    return serialize_db_incident(doc)


