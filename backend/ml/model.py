"""Model training and management for Isolation Forest"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from pathlib import Path
from typing import Optional


MODEL_DIR = Path(__file__).parent
MODEL_PATH = MODEL_DIR / "isolation_forest.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"


def train_model(X: pd.DataFrame, n_estimators: int = 100, contamination: float = 0.05) -> None:
    """
    Train Isolation Forest model on feature data.
    
    Args:
        X: Feature matrix (pandas DataFrame)
        n_estimators: Number of trees in forest
        contamination: Expected proportion of anomalies (0.05 = 5%)
    """
    # Remove non-feature columns
    feature_cols = [col for col in X.columns if not col.startswith("_")]
    X_features = X[feature_cols].fillna(0.0)
    
    # Train model
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,  # Use all cores
    )
    
    model.fit(X_features)
    
    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model trained and saved to {MODEL_PATH}")


def load_model() -> Optional[IsolationForest]:
    """
    Load pre-trained Isolation Forest model.
    
    Returns:
        Loaded model or None if not found
    """
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None


def model_exists() -> bool:
    """Check if model file exists."""
    return MODEL_PATH.exists()


def get_model_info() -> dict:
    """Get information about trained model."""
    if not model_exists():
        return {"status": "not_trained", "path": str(MODEL_PATH)}
    
    model = load_model()
    return {
        "status": "ready",
        "path": str(MODEL_PATH),
        "n_estimators": model.n_estimators,
        "contamination": model.contamination,
    }
