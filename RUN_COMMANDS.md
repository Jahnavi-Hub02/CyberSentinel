# CyberSentinel - Running the Project

This project consists of:
- **Backend**: FastAPI server (port 8000)
- **Frontend**: Streamlit application (port 8501)
- **Database**: MongoDB (port 27017)
- **Admin UI**: Mongo Express (port 8081)

---

## Option 1: Using Docker Compose (Recommended)

This is the easiest way to run the entire project.

### Prerequisites
- Docker Desktop installed and running
- Docker Compose installed

### Steps

1. **Navigate to the project root directory:**
   ```powershell
   cd "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel"
   ```

2. **Create a `.env` file** (optional, MongoDB will use defaults if not provided):
   ```powershell
   # Create .env file with MongoDB configuration
   echo "MONGODB_URI=mongodb://mongo:27017" > .env
   echo "MONGODB_DB=cybersentinel" >> .env
   ```

3. **Start all services:**
   ```powershell
   docker-compose up --build
   ```

   Or run in detached mode (background):
   ```powershell
   docker-compose up --build -d
   ```

4. **Access the applications:**
   - Frontend (Streamlit): http://localhost:8501
   - Backend API: http://localhost:8000
   - API Health Check: http://localhost:8000/api/health
   - API Docs: http://localhost:8000/docs
   - Mongo Express (Admin UI): http://localhost:8081

5. **Stop all services:**
   ```powershell
   docker-compose down
   ```

   To also remove volumes (clears database):
   ```powershell
   docker-compose down -v
   ```

---

## Option 2: Manual Setup (Without Docker)

Run each component separately on your machine.

### Prerequisites
- Python 3.11+ installed
- MongoDB installed and running locally
- pip installed

### Step 1: Start MongoDB

**If MongoDB is installed as a Windows service**, it should be running automatically. Otherwise:

```powershell
# Start MongoDB service (if installed but not running)
net start MongoDB
```

Or if you have MongoDB installed manually, navigate to its bin directory and run:
```powershell
mongod --dbpath "C:\path\to\your\data\db"
```

### Step 2: Setup Backend

1. **Navigate to backend directory:**
   ```powershell
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional, defaults will be used):
   ```powershell
   $env:MONGODB_URI="mongodb://localhost:27017"
   $env:MONGODB_DB="cybersentinel"
   ```

5. **Run the backend server:**
   ```powershell
   python main.py
   ```
   
   Or using uvicorn directly:
   ```powershell
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The backend should start on http://localhost:8000

### Step 3: Setup Frontend

1. **Open a new terminal/PowerShell window**

2. **Navigate to frontend directory:**
   ```powershell
   cd "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel\frontend"
   ```

3. **Create a virtual environment (recommended):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Set API URL** (if backend is on a different host/port):
   ```powershell
   $env:API_URL="http://localhost:8000"
   ```

6. **Run the Streamlit app:**
   ```powershell
   streamlit run app.py
   ```
   
   Or with explicit port:
   ```powershell
   streamlit run app.py --server.port 8501
   ```

   The frontend should start on http://localhost:8501

---

## Quick Start Commands Summary

### Docker Compose (All-in-One)
```powershell
# Start everything
docker-compose up --build

# Start in background
docker-compose up --build -d

# Stop everything
docker-compose down
```

### Manual Setup (Two Terminals)

**Terminal 1 - Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

---

## Troubleshooting

### Docker Desktop Not Running

**Error:** `unable to get image... The system cannot find the file specified` or `open //./pipe/dockerDesktopLinuxEngine`

**Solution:**

1. **Check if Docker Desktop is running:**
   ```powershell
   docker version
   ```
   If this fails, Docker Desktop is not running.

2. **Start Docker Desktop:**
   ```powershell
   # Option 1: Start from Start Menu (recommended)
   # Search for "Docker Desktop" and launch it
   
   # Option 2: Start via PowerShell (if installed in default location)
   Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   
   # Option 3: Check Docker service status
   Get-Service docker
   Start-Service docker
   ```

3. **Wait for Docker Desktop to fully start** (30-60 seconds). Look for the whale icon in the system tray.

4. **Verify Docker is running:**
   ```powershell
   docker ps
   ```

5. **Use the startup script:**
   ```powershell
   .\start-docker.ps1
   ```

### Port Already in Use
If ports 8000, 8501, or 27017 are already in use:
- **Docker**: Change ports in `docker-compose.yml`
- **Manual**: Stop the conflicting service or change port in the command

### MongoDB Connection Issues
- Verify MongoDB is running: `mongosh` or check service status
- For Docker: MongoDB runs automatically in the container
- For manual: Ensure MongoDB service is started

### Module Not Found Errors
- Ensure virtual environments are activated
- Reinstall dependencies: `pip install -r requirements.txt`

### CORS Issues
- Backend already has CORS middleware configured for all origins
- If issues persist, check the FastAPI CORS settings in `backend/main.py`

### Docker Compose Version Warning
- The `version` field in `docker-compose.yml` is obsolete in newer Docker Compose versions
- This is just a warning and can be ignored, or remove the `version: "3.9"` line from the file

---

## Project Structure
```
CyberSentinel/
├── backend/          # FastAPI backend
├── frontend/         # Streamlit frontend
├── data/            # CSV data files
├── docker-compose.yml
└── .env             # Environment variables (create if needed)
```

