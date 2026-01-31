"""ML training pipeline (moved from ml/trainer.py)"""
import pandas as pd
from typing import List, Dict, Any
from .features import extract_features, normalize_features
from .model import train_model

def train_from_incidents(incidents: List[Dict[str, Any]]) -> None:
	# ...existing code from ml/trainer.py...

def retrain_from_csv(csv_path: str) -> None:
	# ...existing code from ml/trainer.py...
