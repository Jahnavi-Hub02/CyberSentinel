"""Feature extraction for anomaly detection"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any


def extract_features(incidents: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Extract ML features from incident data.
    
    Features:
    - temporal: hour of day when incident occurred
    - volumetric: request rate by location/source
    - categorical: incident type encoded
    
    Args:
        incidents: List of incident dictionaries
        
    Returns:
        DataFrame with features ready for model input
    """
    if not incidents:
        return pd.DataFrame()
    
    df = pd.DataFrame(incidents)
    
    # Ensure timestamp is datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hour"] = df["timestamp"].dt.hour
    else:
        df["hour"] = 0
    
    # Incident type encoding (higher numeric value = more critical)
    incident_type_severity = {
        "phishing": 0.3,
        "malware": 0.5,
        "data breach": 0.8,
        "ransomware": 0.9,
        "hacking": 0.7,
        "ddos": 0.6,
        "defacement": 0.4,
    }
    
    if "Incident_Type" in df.columns:
        df["incident_type_score"] = df["Incident_Type"].str.lower().map(
            lambda x: incident_type_severity.get(x, 0.5) if isinstance(x, str) else 0.5
        )
    elif "category" in df.columns:
        df["incident_type_score"] = df["category"].str.lower().map(
            lambda x: incident_type_severity.get(x, 0.5) if isinstance(x, str) else 0.5
        )
    else:
        df["incident_type_score"] = 0.5
    
    # Volumetric feature: count incidents by location
    if "location" in df.columns:
        df["location_incident_count"] = df.groupby("location")["location"].transform("count")
        # Normalize to 0-1 range
        max_count = df["location_incident_count"].max()
        if max_count > 0:
            df["location_incident_count"] = df["location_incident_count"] / max_count
    else:
        df["location_incident_count"] = 0.5
    
    # Amount lost (normalized)
    if "amount_lost" in df.columns:
        amount_lost = pd.to_numeric(df["amount_lost"], errors="coerce").fillna(0)
        max_amount = amount_lost.max()
        if max_amount > 0:
            df["amount_lost_normalized"] = amount_lost / max_amount
        else:
            df["amount_lost_normalized"] = 0.0
    else:
        df["amount_lost_normalized"] = 0.0
    
    # Severity feature (if available)
    severity_score = {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.8,
        "critical": 1.0,
    }
    
    if "severity" in df.columns:
        df["severity_score"] = df["severity"].str.lower().map(
            lambda x: severity_score.get(x, 0.5) if isinstance(x, str) else 0.5
        )
    else:
        df["severity_score"] = 0.5
    
    # Time-based anomaly: incidents at unusual hours (0-6 AM)
    df["off_hours"] = (df["hour"] < 6).astype(float)
    
    # Feature matrix for model
    feature_cols = [
        "incident_type_score",
        "location_incident_count",
        "amount_lost_normalized",
        "severity_score",
        "off_hours",
        "hour"
    ]
    
    X = df[feature_cols].fillna(0.0)
    
    # Add original data for reference
    X["_incident_id"] = df.index if "id" not in df.columns else df["id"]
    X["_original_data"] = [dict(row) for _, row in df.iterrows()]
    
    return X


def normalize_features(X: pd.DataFrame) -> pd.DataFrame:
    """Normalize features to 0-1 range."""
    X_norm = X.copy()
    for col in X.columns:
        if col not in ["_incident_id", "_original_data"]:
            min_val = X[col].min()
            max_val = X[col].max()
            if max_val > min_val:
                X_norm[col] = (X[col] - min_val) / (max_val - min_val)
            else:
                X_norm[col] = 0.0
    return X_norm
