"""Detection logic using trained model (moved from ml/detector.py)"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple

def detect_anomalies(model, X: pd.DataFrame) -> List[Dict[str, Any]]:
	# ...existing code from ml/detector.py...

def calculate_severity(anomaly_score: float) -> str:
	# ...existing code from ml/detector.py...

def calculate_risk_level(anomaly_score: float, incident_severity: str = "MEDIUM") -> str:
	# ...existing code from ml/detector.py...

def enrich_incident(incident: Dict[str, Any], detection_result: Dict[str, Any]) -> Dict[str, Any]:
	# ...existing code from ml/detector.py...
