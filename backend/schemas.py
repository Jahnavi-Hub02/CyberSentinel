"""
Data schemas for the application.

These classes define the canonical shape of data used across:
- ingestion
- detection
- scoring
- alerts
- dashboard consumption

No business logic should live here.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Incident:
    """
    Represents a detected cyber incident.
    This structure is intentionally aligned with what the UI expects.
    """

    id: str
    title: str
    category: str
    severity: str
    location: str
    timestamp: datetime

    # Detection metadata
    anomaly_score: float

    # Lifecycle
    status: str = "Active"

    # Optional enrichment
    source: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Incident into a JSON-serializable dictionary.
        """
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class Alert:
    """
    Represents an alert generated from an incident.
    Alerts are side-effects; they do not replace incidents.
    """

    incident_id: str
    level: str
    message: str
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "level": self.level,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }
