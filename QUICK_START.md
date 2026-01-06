# Quick Start Guide - CyberSentinel

## 🚀 Fastest Way to Run the Project

### Step 1: Fix and Setup (Run Once)
```powershell
cd "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel"
.\fix-and-test.ps1
```

### Step 2: Start Backend (Terminal 1)
```powershell
.\start-backend.ps1
```
Wait until you see: `Application startup complete`

### Step 3: Start Frontend (Terminal 2)
```powershell
.\start-frontend.ps1
```

### Step 4: Open Browser
Visit: **http://localhost:8501**

---

## ✅ Verify Everything Works

1. **Backend Health Check:**
   - Open: http://localhost:8000/api/health
   - Should show: `{"status": "ok"}`

2. **Frontend Pages:**
   - Home - Should load with hero section
   - Dashboard - Shows statistics and map
   - Incidents - Lists all incidents
   - Admin - Shows management tools
   - Profile - User settings

3. **API Documentation:**
   - Open: http://localhost:8000/docs
   - Interactive API explorer

---

## 🔧 If Something Doesn't Work

### Backend Not Starting?
- Check MongoDB is running (if using local MongoDB)
- Check port 8000 is free: `netstat -ano | findstr :8000`
- See backend terminal for error messages

### Frontend Shows Error?
- Check backend is running (should see health check success)
- Check browser console (F12) for errors
- Verify API URL in error message is `http://localhost:8000`

### Still Getting "api:8000" Error?
- Delete `.env` file and recreate from `.env.example`
- Restart frontend after changing `.env`
- Clear browser cache

---

## 📋 All Available Scripts

- `fix-and-test.ps1` - Setup and verify everything
- `start-backend.ps1` - Start backend server
- `start-frontend.ps1` - Start frontend server
- `start-docker.ps1` - Start everything with Docker

---

## 🎯 What Was Fixed

✅ API URL automatically detects local vs Docker environment  
✅ Intelligent fallback to localhost when running locally  
✅ Better error messages  
✅ All pages working correctly  
✅ Startup scripts for easy running  

For detailed information, see: `COMPREHENSIVE_FIX_SUMMARY.md`

