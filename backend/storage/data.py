"""Centralized data access and CSV loading for CyberSentinel backend."""
import os
import pandas as pd
from functools import lru_cache
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
CSV_PATH = os.path.join(DATA_DIR, 'cybersecurity_cases_india_combined.csv')

@lru_cache(maxsize=1)
def load_incidents_csv() -> pd.DataFrame:
    """Load and cache the main incidents CSV as a DataFrame."""
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()
    return pd.read_csv(CSV_PATH, low_memory=False)

# Add more data access functions as needed (e.g., for Mongo fallback)
