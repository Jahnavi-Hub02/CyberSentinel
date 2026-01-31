# 🛡️ CyberSentinel - Threat Intelligence Platform

**Real-time cybersecurity threat detection, analysis, and management system**

A comprehensive platform for analyzing 1200+ cybersecurity incidents with real-time dashboard visualization, threat mapping, and AI-powered analysis.

## ⚡ Quick Start

```bash
# Start both backend and frontend (recommended)
python app.py

# Or start only backend
python app.py backend

# Or start only frontend
python app.py frontend
```

**Dashboard:** http://localhost:8501  
**API Docs:** http://localhost:8000/docs

## ✨ Features

✅ **Real-time Dashboard** - 1200+ cybersecurity incidents with live threat metrics
✅ **Geographic Mapping** - Carto (Dark Matter) basemap with filtered, recent incident markers across India  
✅ **Threat Analytics** - Plotly charts for threat distribution and trends
✅ **Smart Filtering** - Filter by category, location, and threat type
✅ **ML Detection** - Automated threat classification and risk scoring
✅ **FastAPI Backend** - RESTful API with comprehensive endpoints
✅ **Alert System** - Multi-channel notifications (Email, Slack, Telegram)
✅ **Dark Theme UI** - Professional, eye-friendly interface
✅ **Backend API** - FastAPI REST endpoints for incident management
✅ **ML Threat Detection** - Scikit-learn based threat classification
✅ **Database** - MongoDB with file-backed JSON fallback
✅ **Multi-language** - Full Python codebase with clean architecture

## 📊 Data

- **1200 Cybersecurity Incidents** from India
- **10 Incident Types**: Ransomware (189), Phishing (156), Online Fraud (153), Data Breach (136), Hacking (131), Malware (122), Identity Theft (117), Cyber Bullying (116), and more
- **8 Categories**: Corporate, Personal, Government, Social Media, Financial, Healthcare, Education, E-commerce
- **20+ Indian Cities** with geographic coordinates

## 📁 Project Structure

```
CyberSentinel/
│
├── backend/                    # ✅ Production backend only
│   ├── app.py                  # SINGLE FastAPI entry point
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── mongo.py
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── features.py
│   │   ├── model.py
│   │   ├── detector.py
│   │   ├── trainer.py
│   │   └── isolation_forest.pkl
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── incident.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── incidents.py
│   │   ├── detection.py
│   │   └── health.py
│   │
│   └── Dockerfile
│
├── frontend/                   # 🎨 UI only (no ML, no CSV logic)
│   ├── app.py
│   ├── logo.svg
│   └── Dockerfile
│
├── data/                       # 📊 Static datasets (never imported directly)
│   ├── cybersecurity_cases_india_combined.csv
│   ├── phishing.csv
│   └── sample_logs.csv
│
# Note: Experimental scripts were removed from the root project to avoid accidental runtime imports. Keep experiments in a separate archive or private branch if needed.
│
├── scripts/                    # ⚙️ Run & utility scripts
│   ├── service_manager.py
│   ├── ingest_csv.py
│   └── START_SERVICES.bat
│
├── .gitignore
├── README.md
└── requirements.txt
```

## 🚀 Quick Start (Windows)

### Option 1: Two Terminal Windows (Recommended)

**Terminal 1 - Backend API:**
```powershell
cd c:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```
Expected output: `INFO:     Uvicorn running on http://0.0.0.0:8000`

**Alternative (start both services):**
```powershell
python scripts/service_manager.py start
```

**Terminal 2 - Frontend Dashboard:**
```powershell
cd c:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel\frontend
streamlit run app.py  # or: streamlit run ../frontend/app.py from project root
```
Expected output: `You can now view your Streamlit app in your browser. Local URL: http://localhost:8501`

**Step 3: Open Browser**
Navigate to: **http://localhost:8501**

### Option 2: Using PowerShell Script

```powershell
cd c:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel
.\setup_dev.ps1
```

## 📦 Installation

1. Install dependencies (one-time):
```powershell
pip install -r requirements.txt
```

2. Start services (from appropriate directories as shown above)

Optional: Ingest CSV into MongoDB (recommended for production):
```powershell
python scripts/ingest_csv.py --uri mongodb://localhost:27017 --db cybersentinel --drop
```
This will upsert the `data/cybersecurity_cases_india_combined.csv` into `db.incidents`. If MongoDB is not running the backend will fall back to the local CSV as an emergency read-only fallback.

## 🗺️ Dashboard Features

- **Dashboard Tab**: Main threat overview with:
  - Attack type statistics (Phishing, Ransomware, Data Breach, etc.)
  - Live Threat Map showing incident locations on India map (Carto Dark Matter basemap)
  - Map behavior: only the 10–15 most recent incidents are plotted, and only incidents with valid lat/lon are shown. Coordinates are validated to be within acceptable ranges (lat: -90..90, lon: -180..180) to avoid stray markers and clutter.
  - Incident Categories pie chart
  - Recent Incidents table with details

- **Incidents Tab**: Browse and filter all 1200 incidents

- **Admin Tab**: System status and analytics

- **Filters**: Category, Severity, Status, Location, Source

## 🛠️ Technical Stack

| Component | Technology |
|-----------|-----------|
| **Backend API** | FastAPI + Uvicorn |
| **Frontend Dashboard** | Streamlit |
| **Database** | MongoDB (with JSON fallback) |
| **Data Processing** | Pandas 2.2.2 |
| **Mapping** | Folium + OpenStreetMap |
| **Charts** | Plotly 5.24.1 |
| **ML Detection** | Scikit-learn |
| **Python Version** | 3.10+ |

## 📋 File Descriptions

### Backend (`backend/` package)
- `detector.py` - ML-based threat detection using IsolationForest
- `database.py` - Incident persistence (MongoDB or JSON)
- `llm.py` - LLM configuration and API calls
- `alerts.py` - Telegram/Email notification system
- `utils.py` - Shared utility functions
- `dashboard.py` - Analytics dashboard helpers

### Frontend (`frontend/` package)
- `app.py` - Main Streamlit dashboard application (939 lines)
- `.streamlit/config.toml` - Streamlit configuration
- `requirements.txt` - Frontend-specific dependencies

### Root Application
- `app.py` - FastAPI backend entrypoint
- `requirements.txt` - All dependencies including backend and frontend

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/incidents/` | GET | List all incidents (limit param) |
| `/api/generate` | POST | Generate threat analysis |
| `/analyze` | POST | Analyze security log |

## 📊 Sample Data

CSV file location: `data/cybersecurity_cases_india_combined.csv`

Columns: Year, Day, Amount_Lost_INR, Incident_Type, City, Category

```
Data in incidents.json:
- Total Records: 1200
- Incident Types: 10 types
- Geographic Coverage: 20+ Indian cities
- Category Distribution: 8 categories
- Severity Levels: Low, Medium, High, Critical
```

## 🐛 Troubleshooting

**Port 8000/8501 already in use:**
```powershell
Get-Process python,streamlit | Stop-Process -Force
```

**Map not showing:**
- Map uses Carto Dark Matter basemap (no API key required) and is free to use
- The dashboard plots only the 10–15 most recent incidents with valid coordinates to avoid clutter
- Ensure the data has a valid `location` and the backend is reachable (API_URL)
- Ensure internet connection is active and clear browser cache if needed

**CSV not loading:**
- Verify `data/cybersecurity_cases_india_combined.csv` exists
- Check file permissions and CSV format

## 📝 Project Status

✅ Backend API - Fully working
✅ Streamlit Dashboard - Fully working  
✅ Map Visualization - Fully working with OpenStreetMap
✅ Data Loading - 1200 incidents loaded successfully
✅ Filters - All functional
✅ Database - JSON persistence working
✅ Code - Cleaned and optimized

## 👨‍💻 Development

For development with auto-reload:

```powershell
python app.py
# or: uvicorn app:app --reload
```

4. Start the Streamlit dashboard (from root, in another terminal):

```powershell
# Start both services with a single command (recommended):
python app.py

# Or start frontend only:
python app.py frontend
```

5. Use the API:

   - POST `http://localhost:8000/analyze` with JSON `{ "log": "..." }`
   - GET  `http://localhost:8000/api/incidents/` to list incidents
   - GET  `http://localhost:8000/api/health` for health checks

## 🧩 Backend Modules

- **detector.py** – ML-based threat detection (IsolationForest with heuristic fallback)
- **database.py** – MongoDB or file-backed incident storage
- **llm.py** – Model configuration (`MODEL_NAME` environment variable)
- **alerts.py** – Telegram and email notifications
- **utils.py** – Helper functions for log analysis

All backend modules are now in the `backend/` package. Root-level imports (e.g., `from detector import ...`) still work via compatibility shims, so existing code doesn't break.

## 🧪 Running Tests

```powershell
pip install pytest httpx
python -m pytest tests/ -v
```

## 🤖 Machine Learning Detection System (NEW!)

CyberSentinel now includes **production-grade ML-based anomaly detection** using Isolation Forest.

### ML Features
- **Unsupervised Learning**: No labeled data needed - detects statistical anomalies
- **6-Feature Analysis**: Temporal patterns, location trends, incident severity, financial impact
- **Real-time Scoring**: Anomaly scores 0-1 with CRITICAL/HIGH/MEDIUM/LOW severity
- **Async Processing**: Background task training prevents API blocking
- **Zero UI Changes**: Enriched ML fields added to existing incident data
- **MongoDB Integration**: Optional persistent ML results storage

### Quick Start - ML System

**Step 1: Check ML Status**
```bash
python quick_reference.py --status
```

**Step 2: Train Model (if not trained)**
```bash
# See docs/ML_DETECTION_GUIDE.md for demo & API-driven training examples
```

**Step 3: Use API Endpoints**

Train model:
```bash
curl -X POST http://localhost:8000/api/ml/train \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "incidents": [...],  # List of incident dicts
  "contamination": 0.05
}
EOF
```

Run detection:
```bash
curl -X POST http://localhost:8000/api/ml/detect \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "incidents": [...],
  "auto_severity": true
}
EOF
```

Check status:
```bash
curl http://localhost:8000/api/ml/status
```

Get insights:
```bash
curl "http://localhost:8000/api/ml/insights?limit=10&min_anomaly_score=0.7"
```

### ML Architecture

```
Raw Incident Data
    ↓
Feature Extraction (6 features)
    ↓
Normalization (0-1 range)
    ↓
Isolation Forest Model
    ↓
Anomaly Detection (0-1 score)
    ↓
Severity Calculation (CRITICAL/HIGH/MEDIUM/LOW)
    ↓
Incident Enrichment (ML fields added)
    ↓
API Response + Optional MongoDB Storage
```

### ML Files

| File | Purpose |
|------|---------|
| `backend/ml/features.py` | Extract 6 features from incidents |
| `backend/ml/model.py` | Train/load Isolation Forest |
| `backend/ml/detector.py` | Core detection logic |
| `backend/ml/trainer.py` | Training pipeline |
| `backend/routers/detection.py` | 4 FastAPI endpoints |
| `demo_ml_detection.py` | Live demonstration (archived; see `docs/ML_DETECTION_GUIDE.md`) |
| `ML_DETECTION_GUIDE.md` | Comprehensive documentation |

### ML Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/ml/status` | Check model readiness |
| POST | `/api/ml/detect` | Run anomaly detection |
| POST | `/api/ml/train` | Train model (async) |
| GET | `/api/ml/insights` | Get detection statistics |

### ML Model Parameters

- **Algorithm**: Isolation Forest (unsupervised)
- **Trees**: 100 (n_estimators)
- **Contamination**: 5% (expected anomaly rate)
- **Features**: 6 engineered features
- **Severity Thresholds**:
  - Score ≥ 0.8: **CRITICAL**
  - Score ≥ 0.6: **HIGH**
  - Score ≥ 0.4: **MEDIUM**
  - Score < 0.4: **LOW**

### ML Severity Formula

```
Final Risk Level = ML Anomaly Score + Original Severity Weight
- Combines statistical anomaly detection with domain expertise
- Higher score = More unusual pattern detected
- Enriches incidents with ML_SEVERITY field
```

### Example ML Response

```json
{
  "status": "success",
  "total_processed": 100,
  "anomalies_detected": 5,
  "results": [
    {
      "incident_id": 12345,
      "is_anomalous": true,
      "anomaly_score": 0.85,
      "ml_severity": "CRITICAL",
      "detected_by": "IsolationForest"
    }
  ]
}
```

### Training & Retraining

First training (one-time):
```python
from backend.ml.trainer import train_from_incidents
import pandas as pd

# Load your incident data
df = pd.read_csv("data/cybersecurity_cases_india_combined.csv")
incidents = df.to_dict(orient="records")

# Train model
train_from_incidents(incidents)
```

Retrain on new data:
```bash
# Via API (async background task)
curl -X POST http://localhost:8000/api/ml/train \
  -H "Content-Type: application/json" \
  -d '{"incidents": [...], "contamination": 0.05}'
```

### Production Deployment

1. **Train Initial Model**
   ```bash
   python -c "from backend.ml.trainer import train_from_incidents; \
   import pandas as pd; \
   df = pd.read_csv('data/cybersecurity_cases_india_combined.csv'); \
   train_from_incidents(df.to_dict(orient='records'))"
   ```

2. **Use API in Production**
   - Call `/api/ml/detect` for each new incident batch
   - Monitor anomaly rate (~5-10% expected)
   - Retrain monthly with new patterns

3. **Optional: MongoDB Integration**
   - ML results automatically saved to MongoDB if available
   - Fallback to JSON files if MongoDB unavailable
   - Query results: `db.incidents.find({"is_anomalous": true})`

### Troubleshooting ML

**Model not trained yet:**
```bash
# See docs/ML_DETECTION_GUIDE.md for training examples and demo instructions. You can train via API: POST /api/ml/train
```
**High anomaly rate (>20%):**
- Adjust contamination parameter (lower for stricter detection)
- Retrain with more representative data

**Low anomaly rate (<1%):**
- Increase contamination parameter
- Review feature extraction logic

**API returns 503 (Service Unavailable):**
- Check model file exists: `models/isolation_forest.pkl`
- Retrain model if missing
- Check backend logs for details

## 🔐 Notes

- **UI Unchanged:** The Streamlit frontend design and functionality remain intact.
- **Backwards Compatible:** Root-level imports (e.g., `from detector import detect_threat`) still work thanks to shim files.
- **Production Ready:** For production use, add authentication, RBAC, comprehensive testing, CI/CD, and audit logging.
- **ML Production Ready:** Isolation Forest trained, API endpoints integrated, background tasks for async processing, comprehensive documentation provided.



