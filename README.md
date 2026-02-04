# CyberSentinel — Threat Intelligence Platform

CyberSentinel is a real-time cybersecurity threat intelligence platform focused on Indian incident data.  
It combines a FastAPI backend with a Streamlit frontend to give security teams a single pane of glass for:

- Exploring incidents  
- Monitoring geographic hot spots  
- Tracking trends and impact over time  
- Experimenting with ML-based anomaly detection  

The project is designed to be:

- Easy to run locally (CSV fallback, no database required)
- Simple to containerize and deploy
- Extensible for custom data sources and analytics

---

## Screenshots

> Save your screenshots into a `docs/` folder in the repo (for example `docs/home.png` and `docs/dashboard.png`) or adjust the paths below to wherever you store them.

### Home / Landing Page

![CyberSentinel Home](docs/home.png)

### Dashboard View

![CyberSentinel Dashboard](docs/dashboard.png)

---

## Features

- **Real-time dashboard**
  - Live incident table with filters by category, severity, status, and location
  - Summary cards (phishing, ransomware, data breach, malware, hacking, total attacks)

- **Geographic visualization**
  - Interactive threat map centered on India
  - City-level clustering using Plotly mapbox
  - Server-side and client-side geocoding for common Indian cities

- **Standardized incident API**
  - REST API for listing, filtering, and (when DB is enabled) creating incidents
  - CSV fallback mode for instant local setup without MongoDB

- **Analytics and insights**
  - Top locations by incident count
  - Time-series incident trends
  - Category and severity distributions

- **Health & observability**
  - Health endpoints for readiness checks
  - Admin view showing backend/API status and basic environment info

- **ML-ready**
  - Isolation Forest model and feature pipeline (for anomaly / threat scoring)
  - Clean separation between data loading, feature engineering, and model code

---

## Tech Stack

- **Backend**
  - Python
  - FastAPI
  - Optional MongoDB (with CSV fallback when Mongo is unavailable)
- **Frontend**
  - Streamlit
  - Plotly (map visualization)
  - Altair / built-in Streamlit charts
- **Testing**
  - pytest
  - fastapi.testclient

---

## Project Structure

```text
CyberSentinel-main/
  backend/
    app.py                  # FastAPI application
    routers/
      incidents.py          # /api/incidents endpoints (CSV + Mongo)
      health.py             # /health and /api/health
      insights.py           # /api/insights (top locations etc.)
      detection.py          # ML/detection endpoints
    utils/
      geocode.py            # Simple city → lat/lon geocoder + cache
    ml/                     # Isolation Forest model & features
    models/                 # Pydantic models
    db/
      mongo.py              # MongoDB connection helper (optional)
    data/
      cybersecurity_cases_india_combined.csv  # Primary incidents dataset
      geocode_cache.json    # Persistent geocode cache
    tests/                  # Backend + integration tests

  frontend/
    app.py                  # Streamlit dashboard

  scripts/
    run_services.py         # Starts backend + frontend and keeps them tied together
    START_SERVICES.bat      # Windows helper (optional)
    run_and_open.ps1        # PowerShell helper (optional)

  README.md
  Dockerfile                # Top-level Dockerfile for combined app
```

---

## Data Model & Incident Count

The primary dataset lives in:

- `backend/data/cybersecurity_cases_india_combined.csv`

This CSV has around **1200 rows** of Indian cyber incidents with columns like:

- `Year`
- `Day`
- `Amount_Lost_INR`
- `Incident_Type`
- `City`
- `Category`

The backend’s `load_csv_fallback()` function:

1. Loads the CSV.
2. Skips rows without a valid city (needed for mapping).
3. Normalizes each row into a standard incident schema (id, type, category, timestamp, location, severity, etc.).
4. Generates an incident timestamp from Year + Day.
5. Deduplicates incidents by `(type, timestamp, location)`.

After cleaning and deduplication, the system typically exposes around **1140–1150 incidents** via the API.  
This is **expected** and verified by the test suite (the API count matches `load_csv_fallback()`).

---

## Running Locally

### Prerequisites

- Python 3.10+
- (Optional) MongoDB if you want to persist incidents beyond the CSV

> You do **not** need MongoDB to use the app. If Mongo is unavailable, the backend falls back to the CSV dataset automatically.

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/CyberSentinel.git
cd CyberSentinel-main/CyberSentinel-main
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Run backend and frontend together (recommended)

From the project root (`CyberSentinel-main/CyberSentinel-main`), with the virtualenv active:

```bash
python scripts/run_services.py
```

This will:

- Start the FastAPI backend on `http://127.0.0.1:8000`
- Start the Streamlit frontend on `http://localhost:8501`
- Wire the frontend’s `API_URL` to the backend automatically

Then open the dashboard in your browser:

```text
http://localhost:8501
```

Keep this terminal open while you use the app.  
Press `Ctrl+C` to stop both services.

---

## Running Components Separately (Advanced)

### Backend only

```bash
# From project root, with venv active
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

### Frontend only

If you already have a backend running:

```bash
# From project root, with venv active
streamlit run frontend/app.py --server.port 8501
```

By default, the frontend will try to talk to:

- `API_URL` env var, else
- `BACKEND_URL` env var, else
- `http://localhost:8000`

You can override:

```bash
# Example
$env:API_URL="http://127.0.0.1:8000"        # PowerShell
export API_URL="http://127.0.0.1:8000"      # bash/zsh
```

---

## Configuration

Most local setups work with defaults. Key knobs:

- **CORS origins**: `CORS_ORIGINS` (comma-separated list)
  - Defaults to `http://localhost:8501` and `http://127.0.0.1:8501`.
- **Backend URL for frontend**:
  - `API_URL` or `BACKEND_URL`
  - The frontend automatically rewrites Docker-style `api:8000` hostnames to `http://localhost:8000` when not running inside Docker.
- **MongoDB (optional)**:
  - See `backend/db/mongo.py` for connection details and environment variables.
  - When Mongo is not reachable, the backend gracefully falls back to the CSV dataset.

You can also create a `.env` file in the project root to override defaults.  
The frontend will pick up `.env` from either the repo root or the `frontend/` folder if present.

---

## Testing

From the project root, with the virtualenv active:

```bash
pytest
```

This runs:

- Geocoding tests (`backend/tests/test_geocode.py`)
- Health endpoint tests (`backend/tests/test_health.py`)
- Incidents behavior tests (`backend/tests/test_incidents_recent.py`)
- Insights/ETag behavior tests (`backend/tests/test_insights.py`)
- Integration smoke test (`backend/tests/test_integration_smoke.py`) is **skipped by default**.

To run the integration smoke test (requires a running backend on `127.0.0.1:8000`):

```bash
# Start backend in another terminal, then:
RUN_INTEGRATION=1 pytest backend/tests/test_integration_smoke.py
```

On success you should see something like:

```text
7 passed, 1 skipped
```

---

## How It Works (High-Level Flow)

1. **Data ingestion**
   - For local/demo mode, the backend reads from `cybersecurity_cases_india_combined.csv` and normalizes incidents.
   - Optionally, incidents can be stored/retrieved from MongoDB if configured.

2. **Backend API**
   - `/api/incidents/` lists incidents with filters and `limit` support.
   - `/api/insights/top-locations` provides aggregated stats for UI charts.
   - `/health` and `/api/health` report service status.

3. **Geocoding & enrichment**
   - `backend/utils/geocode.py` maps city names to lat/lon and caches them.
   - Incidents are enriched to always include coordinates when possible.

4. **Frontend dashboard**
   - Fetches incidents and insights from the backend.
   - Normalizes missing fields (`severity`, `status`, `source`) for clean tables and filters.
   - Renders:
     - Summary cards
     - Map (clustered incidents across India)
     - Category/severity charts
     - Recent incidents and admin analytics

---

## Roadmap / Ideas

- Expand geocoding coverage beyond a curated city list.
- Plug in a real MongoDB deployment for persistent storage in production.
- Extend ML module with more advanced models and explainability.
- Add authentication and role-based access control for the admin area.
- Containerized local stack with Docker Compose (API + DB + frontend).

---

## License

Add your license here (e.g. MIT, Apache 2.0).

# CyberSentinel — Threat Intelligence Platform

CyberSentinel is a real-time cybersecurity threat intelligence platform built for rapid incident analysis, visualization, and operational monitoring. It combines a FastAPI backend with a Streamlit dashboard to provide a single pane of glass for security teams. The project is designed to be easy to run locally, straightforward to containerize, and simple to extend.

## Project Overview
CyberSentinel ingests incident data (CSV fallback or MongoDB), normalizes it into a consistent schema, and surfaces insights through a live dashboard. The backend exposes a clean REST API, while the frontend visualizes incidents, severity trends, and geographic distribution.

## Features
- **Real-time dashboard** with interactive incident exploration
- **Standardized incident API** for reliable integrations
- **Geographic visualization** of incidents across India
- **Health checks** for service readiness monitoring
- **CSV fallback** when MongoDB is unavailable
- **Developer-friendly setup** with one-click VS Code task
- **CI-ready workflow** for automated tests and linting


## Folder Structure
```
CyberSentinel/

Create a `.env` file in the repo root if you want to override defaults.

## Running the Backend
```bash
# FastAPI (local dev)
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

**Health check:** `GET http://127.0.0.1:8000/health`

## Running the Frontend
```bash

```

Open: **http://localhost:8501**


