# How to Fix "Backend unavailable" Message

## What This Message Means

When you see **"Backend unavailable. Using local dataset (6 incidents)"**, it means:
- ✅ Your frontend is working correctly
- ✅ It's successfully loading data from the local CSV file
- ⚠️ The backend API server is not running

## Quick Fix: Start the Backend

### Option 1: Using Startup Script (Easiest)

1. **Open a NEW PowerShell terminal** (keep the frontend terminal running)
2. Navigate to project:
   ```powershell
   cd "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel"
   ```
3. Run the startup script:
   ```powershell
   .\start-backend.ps1
   ```

### Option 2: Manual Start

1. **Open a NEW PowerShell terminal**
2. Navigate to backend:
   ```powershell
   cd "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel\backend"
   ```
3. Activate virtual environment (if not already):
   ```powershell
   & "..\..venv\Scripts\Activate.ps1"
   ```
4. Start the server:
   ```powershell
   python main.py
   ```

## Verify Backend is Running

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Test Backend Connection

In a browser or PowerShell, test:
```powershell
curl http://localhost:8000/api/health
```

Should return: `{"status": "ok"}`

## After Backend Starts

1. **Go back to your frontend** (Streamlit app)
2. **Click "🔄 Try Reconnecting"** button in the expandable message
3. The message should disappear and you'll see data from the backend

## Why Two Terminals?

- **Terminal 1**: Runs the frontend (Streamlit) - port 8501
- **Terminal 2**: Runs the backend (FastAPI) - port 8000

Both need to run simultaneously for full functionality.

## Troubleshooting

### Backend won't start?
- Check if port 8000 is already in use
- Check MongoDB is running (if using local MongoDB)
- Check backend logs for errors

### Backend starts but frontend still shows error?
- Verify backend is accessible: `curl http://localhost:8000/api/health`
- Check API URL in frontend matches backend URL
- Clear browser cache
- Click "Refresh Connection" button in frontend

### Want to use Docker instead?
```powershell
docker-compose up --build
```
This starts everything (backend, frontend, MongoDB) together.

