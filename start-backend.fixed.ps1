param()

# Simple, robust backend starter for CyberSentinel
Write-Host "=== Starting CyberSentinel Backend ===" -ForegroundColor Cyan

$projectRoot = "C:\Users\jaanu\OneDrive\Desktop\FINAL PROJECT\CyberSentinel"
Set-Location $projectRoot

# Activate virtual environment if it exists
$venvPath = Join-Path $projectRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "âœ" Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "âš  No .venv found at $venvPath, using current Python environment" -ForegroundColor Yellow
}

# Navigate to backend folder
Set-Location backend
Write-Host "Backend working directory: $(Get-Location)" -ForegroundColor DarkGray

Write-Host ""
Write-Host "Starting backend server on http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload



