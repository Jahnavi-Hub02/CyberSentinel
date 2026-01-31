"""Anomaly detection using trained Isolation Forest model"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple


def detect_anomalies(model, X: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Run anomaly detection on feature matrix.
    
    Returns predictions with anomaly scores.
    
    Args:
        model: Trained Isolation Forest model
        X: Feature matrix
        
    Returns:
        List of detection results with scores
    """
    # Extract feature columns (skip metadata)
    feature_cols = [col for col in X.columns if not col.startswith("_")]
    X_features = X[feature_cols].fillna(0.0)
    
    # Get predictions and scores
    predictions = model.predict(X_features)  # -1 for anomaly, 1 for normal
    scores = model.score_samples(X_features)  # Raw anomaly scores
    
    # Convert to 0-1 anomaly score (higher = more anomalous)
    # score_samples returns negative values for anomalies
    anomaly_scores = -scores
    anomaly_scores = (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min() + 1e-8)
    
    results = []
    for idx, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
        results.append({
            "is_anomaly": bool(int(pred) == -1),
            "anomaly_score": float(score),
            "raw_prediction": int(pred),
        })
    
    return results


def calculate_severity(anomaly_score: float) -> str:
    """
    Convert anomaly score to severity level.
    
    Args:
        anomaly_score: Score between 0 and 1
        
    Returns:
        Severity level: LOW, MEDIUM, HIGH, CRITICAL
    """
    if anomaly_score >= 0.8:
        return "CRITICAL"
    elif anomaly_score >= 0.6:
        return "HIGH"
    elif anomaly_score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"


def calculate_risk_level(anomaly_score: float, incident_severity: str = "MEDIUM") -> str:
    """
    Calculate overall risk level combining ML score and incident severity.
    
    Args:
        anomaly_score: ML-based anomaly score (0-1)
        incident_severity: Original incident severity
        
    Returns:
        Risk level: LOW, MEDIUM, HIGH, CRITICAL
    """
    # Combine ML score with existing severity
    severity_weight = {
        "LOW": 0.2,
        "MEDIUM": 0.5,
        "HIGH": 0.8,
        "CRITICAL": 1.0,
    }
    
    base_severity = severity_weight.get(incident_severity.upper(), 0.5)
    combined_score = 0.6 * anomaly_score + 0.4 * base_severity
    
    return calculate_severity(combined_score)


def enrich_incident(incident: Dict[str, Any], detection_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich incident with ML detection results.
    
    Args:
        incident: Original incident dictionary
        detection_result: Detection result from model
        
    Returns:
        Enriched incident with ML fields
    """
    enriched = incident.copy()
    
    anomaly_score = float(detection_result["anomaly_score"])
    enriched["anomaly_score"] = anomaly_score
    enriched["is_anomalous"] = bool(detection_result["is_anomaly"])
    enriched["ml_severity"] = calculate_severity(anomaly_score)
    enriched["detected_by"] = "ML-IsolationForest"
    
    # Update overall severity to be the maximum of original and ML-detected
    original_severity = enriched.get("severity", "MEDIUM").upper()
    ml_severity = enriched["ml_severity"].upper()
    
    severity_priority = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    if severity_priority.get(ml_severity, 0) > severity_priority.get(original_severity, 0):
        enriched["severity"] = ml_severity
    
    return enriched
