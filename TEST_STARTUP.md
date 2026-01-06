# Testing Startup Scripts

## Fixed Issues

The startup scripts have been updated to:
1. Use proper path resolution with `Join-Path`
2. Check if venv is already activated
3. Continue gracefully if venv not found but environment is already set up
4. Always install/upgrade dependencies to ensure everything is current

## Quick Test

Run these commands one by one:

### Test Backend Startup
```powershell
cd "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel"
.\start-backend.ps1
```

**Expected output:**
- ✓ Virtual environment activated
- ✓ Dependencies ready
- Starting backend server on http://localhost:8000

### Test Frontend Startup (in a new terminal)
```powershell
cd "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel"
.\start-frontend.ps1
```

**Expected output:**
- ✓ Virtual environment activated
- ✓ Dependencies ready
- API URL: http://localhost:8000
- Starting frontend server on http://localhost:8501

## Troubleshooting

If scripts still fail:

1. **Check if .venv exists:**
   ```powershell
   Test-Path ".\.venv\Scripts\Activate.ps1"
   ```

2. **Manually activate venv:**
   ```powershell
   & ".\.venv\Scripts\Activate.ps1"
   ```

3. **Run backend manually:**
   ```powershell
   cd backend
   python main.py
   ```

4. **Run frontend manually:**
   ```powershell
   cd frontend
   python -m streamlit run app.py
   ```

## Notes

- Scripts now work even if venv is already activated
- Scripts continue if venv path check fails (assumes environment is already set up)
- Dependencies are always checked and upgraded

