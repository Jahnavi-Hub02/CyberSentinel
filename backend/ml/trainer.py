"""Training pipeline for ML models"""
import pandas as pd
from typing import List, Dict, Any
from .features import extract_features, normalize_features
from .model import train_model


def train_from_incidents(incidents: List[Dict[str, Any]]) -> None:
    """
    Full training pipeline: extract features from incidents, train model.
    
    Args:
        incidents: List of incident records
    """
    if not incidents or len(incidents) < 10:
        print("⚠️ Need at least 10 incidents to train model")
        return
    
    print(f"📊 Training on {len(incidents)} incidents...")
    
    # Extract features
    X = extract_features(incidents)
    print(f"✅ Extracted {len(X.columns)} features from incidents")
    
    # Normalize features
    X_normalized = normalize_features(X)
    
    # Remove metadata columns for training
    feature_cols = [col for col in X_normalized.columns if not col.startswith("_")]
    X_train = X_normalized[feature_cols]
    
    # Train model
    contamination = min(0.1, max(0.02, len(incidents) / 1000))
    train_model(X_train, contamination=contamination)
    print(f"✅ Model training complete (contamination={contamination:.2%})")


def retrain_from_csv(csv_path: str) -> None:
    """
    Retrain model from CSV data.
    
    Args:
        csv_path: Path to CSV file with incident data
    """
    df = pd.read_csv(csv_path)
    incidents = df.to_dict(orient="records")
    train_from_incidents(incidents)
