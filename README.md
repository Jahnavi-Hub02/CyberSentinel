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


