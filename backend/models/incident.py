from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Incident(BaseModel):
    """Standardized incident payload returned by the API."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(..., description="Incident identifier (INC-xxxx)")
    type: str = Field(..., description="Incident type, e.g. Phishing")
    category: str
    severity: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: str
    timestamp: str = Field(..., description="ISO-8601 timestamp in UTC")


class IncidentCreate(BaseModel):
    """Request payload for creating a new incident."""

    type: str
    category: str
    severity: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: str
    timestamp: Optional[str] = None

