# CyberSentinel — Threat Intelligence Platform

CyberSentinel is a real-time cybersecurity threat intelligence platform for monitoring, analyzing, and visualizing incidents. It combines a FastAPI backend with a Streamlit dashboard, providing a clean API and a polished UI for security analysts and engineers.

## Project Overview
CyberSentinel normalizes incident data (MongoDB when available, CSV fallback otherwise) and exposes a consistent REST API. The frontend consumes the API to deliver live charts, map-based threat visualization, and operational status indicators.

## Features
- Real-time incident dashboard with interactive filters
- Standardized incident API responses
- Geographic threat visualization with clustering
- Health checks for service monitoring
- CSV fallback when MongoDB is unavailable
- One-click VS Code task for local dev
- GitHub Actions CI for tests and lint checks

## Tech Stack
- **Backend:** FastAPI, Uvicorn
- **Frontend:** Streamlit, Plotly
- **Data:** Pandas
- **Database:** MongoDB (optional), CSV fallback
- **CI:** GitHub Actions
- **Containers:** Docker

## Folder Structure
```
CyberSentinel/
├── backend/                 # FastAPI backend
│   ├── app.py
│   ├── data/                # CSV fallback data + cache
│   ├── db/                  # MongoDB helpers
│   ├── ml/                  # ML detection components
│   ├── models/              # Pydantic models
│   ├── routers/             # API routes
│   ├── tests/               # Backend tests
│   └── requirements.txt
├── frontend/                # Streamlit dashboard
│   ├── app.py
│   └── logo.svg
├── scripts/                 # Utility scripts
│   ├── run_services.py
│   ├── run_and_open.ps1
│   └── ingest_csv.py
├── .github/                 # CI workflows
├── .vscode/                 # Editor tasks
├── Dockerfile               # Backend container
└── README.md
```

## Prerequisites
- **Python 3.10+**
- **pip**
- (Optional) **MongoDB** for persistence
- (Optional) **Docker** for containerized backend

## Installation
```bash
# 1) Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r backend/requirements.txt
```

## Environment Variables
| Variable | Description | Default |
| --- | --- | --- |
| `API_URL` | Frontend base URL for the backend | `http://localhost:8000` |
| `BACKEND_URL` | Alternate frontend base URL | (none) |
| `MONGODB_URI` | MongoDB connection URI | `mongodb://mongo:27017` |
| `MONGODB_DB` | MongoDB database name | `cybersentinel` |
| `CORS_ORIGINS` | Comma-separated CORS allowlist | `http://localhost:8501,http://127.0.0.1:8501` |

Create a `.env` file in the repo root to override defaults if needed.

## Running the Backend
```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

**Health check:** `GET http://127.0.0.1:8000/health`

## Running the Frontend
```bash
python -m streamlit run frontend/app.py --server.port 8501 --server.headless true
```

Open: **http://localhost:8501**

## Running Both Services (Convenience)
```bash
python scripts/run_services.py
```

## API Endpoints
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Health check (`{ "status": "online" }`) |
| GET | `/api/health` | Health check alias |
| GET | `/api/incidents/` | List incidents (filters + limit) |
| POST | `/api/incidents/` | Create incident (MongoDB required) |
| GET | `/api/insights/top-locations` | Top incident locations |
| GET | `/api/ml/status` | ML model status |
| POST | `/api/ml/train` | Train ML model |
| POST | `/api/ml/detect` | Run detection |
| GET | `/api/ml/insights` | ML insights summary |

## Dev Workflow
### VS Code One-Click Task
Run the repo in VS Code:
1. Open the workspace.
2. **Terminal → Run Task → Dev: Run backend + frontend**.

This task calls `scripts/run_and_open.ps1` to start backend + frontend and open the dashboard.

### CI
GitHub Actions runs on every push and PR:
- Installs dependencies
- Runs `pytest` when tests are present
- Runs `ruff` if configured in `pyproject.toml`

## Docker Usage
Build and run the backend container:
```bash
# Build
docker build -t cybersentinel-backend .

# Run
docker run -p 8000:8000 --env MONGODB_URI=mongodb://host.docker.internal:27017 cybersentinel-backend
```

## Contribution Guide
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-change`.
3. Run tests: `python -m pytest -q backend/tests`.
4. Commit with a clear message.
5. Open a pull request with context and screenshots where applicable.

## License
This project is open source. Review the repository license for terms and conditions.
