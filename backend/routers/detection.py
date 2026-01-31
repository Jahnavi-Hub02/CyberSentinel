"""ML Detection API endpoints"""
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import asyncio
from ..ml.model import load_model, model_exists, get_model_info
from ..ml.features import extract_features, normalize_features
from ..ml.detector import detect_anomalies, enrich_incident
from ..ml.trainer import train_from_incidents


router = APIRouter(tags=["ml-detection"])


class DetectionRequest(BaseModel):
    """Request model for detection"""
    incidents: List[Dict[str, Any]]
    auto_severity: bool = True


class DetectionResponse(BaseModel):
    """Response model for detection"""
    status: str
    total_processed: int
    anomalies_detected: int
    results: Optional[List[Dict[str, Any]]] = None


class TrainingRequest(BaseModel):
    """Request model for training"""
    incidents: List[Dict[str, Any]]
    contamination: Optional[float] = None


@router.get("/ml/status")
async def detection_status() -> Dict[str, Any]:
    """
    Check ML detection system status.
    
    Returns model info and readiness.
    """
    info = get_model_info()
    return {
        "model_status": info,
        "api_ready": model_exists(),
        "message": "ML detection system is ready" if model_exists() else "Model not trained yet. Train with POST /ml/train"
    }


@router.post("/ml/detect", response_model=DetectionResponse)
async def detect_incidents(request: DetectionRequest, background_tasks: BackgroundTasks) -> DetectionResponse:
    """
    Run anomaly detection on incidents.
    
    Uses trained Isolation Forest model to detect unusual patterns.
    Can run in background for large datasets.
    
    Args:
        request: List of incidents and options
        background_tasks: For async processing
        
    Returns:
        Detection results with anomaly scores
    """
    if not model_exists():
        raise HTTPException(
            status_code=503,
            detail="ML model not trained. POST to /ml/train with incident data first."
        )
    
    if not request.incidents:
        raise HTTPException(status_code=400, detail="No incidents provided")
    
    try:
        # Extract and normalize features
        X = extract_features(request.incidents)
        X_normalized = normalize_features(X)
        
        # Load model and run detection
        model = load_model()
        if model is None:
            raise HTTPException(status_code=503, detail="Failed to load model")
        
        detection_results = detect_anomalies(model, X_normalized)
        
        # Enrich incidents with detection results
        enriched_incidents = []
        anomaly_count = 0
        
        for incident, detection in zip(request.incidents, detection_results):
            enriched = enrich_incident(incident, detection)
            enriched_incidents.append(enriched)
            if detection["is_anomaly"]:
                anomaly_count += 1
        
        return DetectionResponse(
            status="success",
            total_processed=len(request.incidents),
            anomalies_detected=anomaly_count,
            results=enriched_incidents
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")


@router.post("/ml/train")
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Train Isolation Forest model on incident data.
    
    Should be called during setup with historical data.
    
    Args:
        request: Training incidents and parameters
        background_tasks: For async training
        
    Returns:
        Training status
    """
    if not request.incidents or len(request.incidents) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 10 incidents to train. Provided: {len(request.incidents)}"
        )
    
    # Run training in background
    background_tasks.add_task(
        train_from_incidents,
        request.incidents
    )
    
    return {
        "status": "training_started",
        "incidents_count": len(request.incidents),
        "message": "Model training started in background. Check /ml/status for progress."
    }


@router.get("/ml/insights")
async def get_insights(
    limit: int = Query(10, ge=1, le=100),
    min_anomaly_score: float = Query(0.5, ge=0.0, le=1.0),
) -> Dict[str, Any]:
    """
    Get insights from last detection results.
    
    Returns:
        - Top anomalies
        - Detection statistics
        - Risk distribution
    """
    return {
        "message": "Insights endpoint - integrate with your MongoDB for real data",
        "parameters": {
            "limit": limit,
            "min_anomaly_score": min_anomaly_score
        },
        "note": "This endpoint can be enhanced to query MongoDB for recent detections"
    }
