# CyberSentinel - Cyber Threat Intelligence Dashboard

A real-time cyber threat intelligence platform for monitoring and managing cybersecurity incidents.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop (optional, for containerized deployment)
- MongoDB (or use Docker for MongoDB)

### Local Development Setup

1. **Activate Virtual Environment**
   ```powershell
   & .\.venv\Scripts\Activate.ps1
   ```

2. **Start Backend** (Terminal 1)
   ```powershell
   .\start-backend.ps1
   ```
   Backend runs on: http://localhost:8000

3. **Start Frontend** (Terminal 2)
   ```powershell
   .\start-frontend.ps1
   ```
   Frontend runs on: http://localhost:8501

4. **Open Browser**
   - Frontend: http://localhost:8501
   - Backend API Docs: http://localhost:8000/docs

## 🐳 Docker Deployment

Run everything with Docker Compose:

```powershell
docker-compose up --build
```

This starts:
- Backend API (port 8000)
- Frontend Streamlit app (port 8501)
- MongoDB (port 27017)
- Mongo Express admin UI (port 8081)

## 📁 Project Structure

```
CyberSentinel/
├── .venv/              # Root virtual environment (shared)
├── .env                # Environment variables
├── backend/            # FastAPI backend
│   ├── main.py        # Application entry point
│   ├── routers/       # API routes
│   ├── models/        # Data models
│   └── db/            # Database configuration
├── frontend/          # Streamlit frontend
│   └── app.py        # Main application
├── data/              # CSV data files
├── start-backend.ps1  # Backend startup script
└── start-frontend.ps1 # Frontend startup script
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
API_URL=http://localhost:8000
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=cybersentinel
```

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/incidents/` - List incidents
- `POST /api/incidents/` - Create incident

See full API documentation at: http://localhost:8000/docs

## 📝 Features

- **Real-time Incident Monitoring**
- **Interactive Threat Map**
- **Incident Management Dashboard**
- **Analytics & Reporting**
- **Admin Panel**
- **User Profile Management**

## 🛠️ Development

### Install Dependencies

All dependencies are consolidated in the root `.venv`:

```powershell
& .\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Testing

- Backend health: `curl http://localhost:8000/api/health`
- Frontend: Open http://localhost:8501 in browser

## 📚 Documentation

- See `CLEANUP_SUMMARY.md` for setup details
- API documentation available at `/docs` endpoint

## 🔐 MongoDB Access

Mongo Express (when using Docker):
- URL: http://localhost:8081
- Default credentials: admin / pass

## 🐛 Troubleshooting

### Backend Not Starting
- Check MongoDB is running
- Verify port 8000 is available
- Check backend logs for errors

### Frontend Shows "Backend unavailable"
- Ensure backend is running on port 8000
- Check API_URL in .env file
- Click "Refresh Connection" in frontend

### Port Already in Use
- Change ports in docker-compose.yml or scripts
- Or stop the conflicting service

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

---

**Status**: ✅ Project is cleaned, organized, and ready for development!

