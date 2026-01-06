from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI(title="CyberSentinel CSV Test API")

# Allow local frontend access (adjust origins if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# path to CSV (project root/data/...)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cybersecurity_cases_india_combined.csv")

def load_df():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"CSV not found at {DATA_PATH}")
    # read with low_memory False to reduce dtype warnings
    df = pd.read_csv(DATA_PATH, low_memory=False)
    return df

@app.get("/api/incidents/")
def read_incidents(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    """
    Returns paginated incidents from CSV as JSON.
    Example: /api/incidents/?limit=100&offset=0
    """
    try:
        df = load_df()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    total = len(df)
    df_slice = df.iloc[offset: offset + limit]
    # convert complex types to strings where needed, fill NaN
    records = df_slice.fillna("").to_dict(orient="records")
    return {"count": total, "limit": limit, "offset": offset, "incidents": records}
