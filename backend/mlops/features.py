"""Feature extraction for anomaly detection (moved from ml/features.py)"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

def extract_features(incidents: List[Dict[str, Any]]) -> pd.DataFrame:
	# ...existing code from ml/features.py...

def normalize_features(X: pd.DataFrame) -> pd.DataFrame:
	# ...existing code from ml/features.py...
