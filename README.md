# CyberSentinel 🛡️

**Cybersecurity Threat Intelligence & Incident Management Platform**

Real-time threat detection, incident visualization, and analysis dashboard for cybersecurity professionals.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009485.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B.svg)](https://streamlit.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ⚡ Quick Start (2 minutes)

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Jahnavi-Hub02/CyberSentinel.git
cd CyberSentinel

# 2. Install dependencies
pip install -r requirements.txt
```

### Running the Application

#### Option A: Frontend Only (Default)
```bash
python main.py
# or
streamlit run app.py
```
→ Opens dashboard at **http://localhost:8501**

#### Option B: Backend API Only
```bash
python main.py --backend
# or
python -m uvicorn backend.main:create_app --reload
```
→ API available at **http://localhost:8000**  
→ API docs at **http://localhost:8000/docs**

#### Option C: Both Backend & Frontend (Two Terminals)
```bash
# Terminal 1
python main.py --backend

# Terminal 2
python main.py --frontend
```

---

## 📊 Features

✅ **Real-time Dashboard** - Interactive incident monitoring and visualization  
✅ **Threat Mapping** - Geographic visualization of security incidents  
✅ **Advanced Filtering** - Filter by category, severity, location, status  
✅ **REST API** - FastAPI with auto-generated docs & Swagger UI  
✅ **MongoDB Integration** - Scalable data persistence  
✅ **Async Operations** - Fast, non-blocking requests  
✅ **Error Handling** - Comprehensive fallback to local data  
✅ **Production Ready** - CORS enabled, health checks, proper logging  

---

## 🏗️ Architecture

```
CyberSentinel/
├── main.py                    # Entry point (backend & frontend launcher)
├── app.py                     # Streamlit app wrapper
├── requirements.txt           # Python dependencies
│
├── backend/
│   ├── main.py               # FastAPI app factory
│   ├── db/
│   │   └── mongo.py          # MongoDB async client
│   ├── models/
│   │   └── incident.py       # Pydantic data models
│   └── routers/
│       └── incidents.py      # API endpoints
│
├── frontend/
│   └── app.py                # Streamlit dashboard (835 lines)
│       ├── Data loading
│       ├── Normalization
│       ├── API communication
│       ├── Visualization
│       └── Interactive filters
│
├── data/
│   └── cybersecurity_cases_india_combined.csv  # 1200+ incidents
│
└── tests/                     # Unit & integration tests
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit 1.38.0 | Interactive web dashboard |
| **Backend** | FastAPI 0.111.0 | REST API server |
| **Server** | Uvicorn | ASGI server |
| **Database** | MongoDB | Incident persistence |
| **Async** | Motor, asyncio | Non-blocking operations |
| **Data** | Pandas, NumPy | Data processing |
| **Viz** | Pydeck, Plotly, Altair | Interactive charts & maps |
| **Python** | 3.11+ | Language runtime |

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/incidents/` | List incidents (filters optional) |
| `POST` | `/incidents/` | Create new incident |
| `GET` | `/docs` | Interactive Swagger UI |
| `GET` | `/redoc` | ReDoc documentation |

### Example Requests

```bash
# Get all incidents
curl http://localhost:8000/api/incidents/

# Filter by category
curl "http://localhost:8000/api/incidents/?category=phishing"

# Filter by severity
curl "http://localhost:8000/api/incidents/?severity=high"
```

---

## 🗄️ Database Setup

### Option 1: MongoDB Atlas (Cloud - Recommended)

1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Set environment variable:
```bash
export MONGODB_URI="mongodb+srv://user:password@cluster.mongodb.net"
export MONGODB_DB="cybersentinel"
```

### Option 2: Local MongoDB (Docker)

```bash
docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password mongo:latest
```

Set environment variables:
```bash
export MONGODB_URI="mongodb://admin:password@localhost:27017"
export MONGODB_DB="cybersentinel"
```

### Option 3: File-Based Fallback

If MongoDB is unavailable, the app automatically loads data from `data/cybersecurity_cases_india_combined.csv`.

---

## 🐳 Docker Deployment

### Run with Docker Compose

```bash
docker-compose up --build
```

Services:
- **Backend API** → http://localhost:8000
- **Frontend Dashboard** → http://localhost:8501
- **MongoDB** → localhost:27017
- **Mongo Express** → http://localhost:8081

---

## 📈 Data Overview

**Dataset**: 1200+ cybersecurity incidents from India

| Metric | Value |
|--------|-------|
| **Total Incidents** | 1200+ |
| **Geographic Coverage** | 20+ Indian cities |
| **Categories** | 8 types |
| **Incident Types** | 10+ types |
| **Date Range** | 2018-2023 |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_api_generate.py -v
```

---

## 🐛 Troubleshooting

### Module not found errors
```bash
cd /path/to/CyberSentinel
python main.py
```

### Port already in use
```bash
# Windows
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

### MongoDB connection failed
Check your connection string and ensure MongoDB is running.

---

## 📝 Code Quality

- ✅ Type hints throughout
- ✅ Comprehensive error handling
- ✅ CORS enabled
- ✅ Async/await for performance
- ✅ Pydantic models for validation
- ✅ Structured logging

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Jahnavi Hub**  
GitHub: [@Jahnavi-Hub02](https://github.com/Jahnavi-Hub02)

---

**Last Updated**: January 2026  
**Version**: 1.0.0

