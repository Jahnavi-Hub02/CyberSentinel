"""Model loading and management (moved from ml/model.py)"""
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
	# ...existing code from ml/model.py...

def load_model() -> Optional[IsolationForest]:
	# ...existing code from ml/model.py...

def model_exists() -> bool:
	# ...existing code from ml/model.py...

def get_model_info() -> dict:
	# ...existing code from ml/model.py...
