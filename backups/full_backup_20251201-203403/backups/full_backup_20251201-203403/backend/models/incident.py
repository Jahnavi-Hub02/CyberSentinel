from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class Incident(BaseModel):
    id: str = Field(..., description="UUID of the incident")
    title: str
    description: str
    category: str
    source: str
    timestamp: datetime
    severity: str
    location: str
    status: str


class IncidentCreate(BaseModel):
    title: str
    description: str
    category: str
    source: str
    timestamp: Optional[datetime] = None
    severity: str
    location: str
    status: str = "Active"


def serialize_db_incident(doc: dict) -> Incident:
    return Incident(
        id=doc.get("id") or str(uuid.uuid4()),
        title=doc["title"],
        description=doc["description"],
        category=doc["category"],
        source=doc["source"],
        timestamp=doc["timestamp"],
        severity=doc["severity"],
        location=doc["location"],
        status=doc.get("status", "Active"),
    )


