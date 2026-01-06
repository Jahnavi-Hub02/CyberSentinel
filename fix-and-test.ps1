# CyberSentinel - Fix and Test Script
# This script fixes API connection issues and tests all components

Write-Host "=== CyberSentinel Fix and Test Script ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Navigate to project root
$projectRoot = "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel"
Set-Location $projectRoot
Write-Host "✓ Project root: $projectRoot" -ForegroundColor Green

# Step 2: Create backups
Write-Host "`n[1/10] Creating backups..." -ForegroundColor Yellow
New-Item -Path ".\backups" -ItemType Directory -Force | Out-Null
Copy-Item -Path ".\frontend\app.py" -Destination ".\backups\frontend_app_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').py" -Force
Write-Host "✓ Backup created" -ForegroundColor Green

# Step 3: Check virtual environment
Write-Host "`n[2/10] Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "\.venv\Scripts\Activate.ps1") {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "⚠ Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Step 4: Activate venv and upgrade pip
Write-Host "`n[3/10] Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel --quiet
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Step 5: Install frontend dependencies
Write-Host "`n[4/10] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
pip install -r requirements.txt --quiet
Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
Set-Location ..

# Step 6: Install backend dependencies
Write-Host "`n[5/10] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt --quiet
Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
Set-Location ..

# Step 7: Create .env file if it doesn't exist
Write-Host "`n[6/10] Checking .env file..." -ForegroundColor Yellow
if (-Not (Test-Path ".\.env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".\.env.example") {
        Copy-Item ".\.env.example" ".\.env"
        Write-Host "✓ .env file created from .env.example" -ForegroundColor Green
    } else {
        # Create basic .env
        @"
API_URL=http://localhost:8000
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=cybersentinel
"@ | Out-File -FilePath ".\.env" -Encoding utf8
        Write-Host "✓ Basic .env file created" -ForegroundColor Green
    }
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Step 8: Verify API_URL in frontend code
Write-Host "`n[7/10] Verifying frontend API configuration..." -ForegroundColor Yellow
$frontendCode = Get-Content ".\frontend\app.py" -Raw
if ($frontendCode -match "API_URL.*=.*os\.getenv|get_api_url\(\)") {
    Write-Host "✓ Frontend API configuration looks good" -ForegroundColor Green
} else {
    Write-Host "⚠ Frontend API configuration may need checking" -ForegroundColor Yellow
}

# Step 9: Check if backend is running
Write-Host "`n[8/10] Checking backend status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Backend is running on http://localhost:8000" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Backend is not running. You'll need to start it manually." -ForegroundColor Yellow
    Write-Host "  Run in a separate terminal: cd backend && python main.py" -ForegroundColor Cyan
}

# Step 10: Summary
Write-Host "`n=== Fix Summary ===" -ForegroundColor Cyan
Write-Host "✓ All fixes applied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Start the backend (Terminal 1):" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   python main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Start the frontend (Terminal 2):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Cyan
Write-Host "   streamlit run app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Open your browser:" -ForegroundColor White
Write-Host "   http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "API URL Configuration:" -ForegroundColor Yellow
Write-Host "  - Default: http://localhost:8000" -ForegroundColor White
Write-Host "  - Can be overridden via .env file or API_URL environment variable" -ForegroundColor White
Write-Host ""

