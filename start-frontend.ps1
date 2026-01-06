# Start Frontend Server
Write-Host "=== Starting CyberSentinel Frontend ===" -ForegroundColor Cyan

$projectRoot = "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel"
Set-Location $projectRoot

# Activate virtual environment if not already activated
$venvPath = Join-Path $projectRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "Virtual environment activated" -ForegroundColor Green
}
else {
    if (-Not $env:VIRTUAL_ENV) {
        Write-Host "Virtual environment not found. Continuing with current Python environment..." -ForegroundColor Yellow
    }
}

# Navigate to frontend
Set-Location frontend

# Install/upgrade dependencies
Write-Host "Checking frontend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet --upgrade
Write-Host "Dependencies ready" -ForegroundColor Green

# Set API URL to localhost if not set
if (-Not $env:API_URL) {
    $env:API_URL = "http://localhost:8000"
}

Write-Host ""
Write-Host "Starting frontend server on http://localhost:8501" -ForegroundColor Green
Write-Host "API URL: $env:API_URL" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start Streamlit
python -m streamlit run app.py
