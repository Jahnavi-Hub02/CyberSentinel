param()

Write-Host "=== Starting CyberSentinel Backend ===" -ForegroundColor Cyan

# Determine script root safely (works when run as a file or from current folder)
if (-not $PSScriptRoot -or $PSScriptRoot -eq "") {
    $ScriptRoot = (Get-Location).Path
} else {
    $ScriptRoot = $PSScriptRoot
}

Write-Host ("Script root: {0}" -f $ScriptRoot) -ForegroundColor DarkGray

# Path to virtual environment activation script
$venvPath = Join-Path $ScriptRoot ".venv\Scripts\Activate.ps1"

if (Test-Path $venvPath) {
    Write-Host ("Activating virtual environment: {0}" -f $venvPath) -ForegroundColor Cyan
    . $venvPath   # dot-source to activate
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host ("WARNING: .venv not found at {0}. Using current Python environment." -f $venvPath) -ForegroundColor Yellow
}

# Navigate to backend folder if it exists
$backendDir = Join-Path $ScriptRoot "backend"
if (Test-Path $backendDir) {
    Set-Location $backendDir
} else {
    Write-Host ("WARNING: Backend folder not found at {0}. Staying in {1}." -f $backendDir, $ScriptRoot) -ForegroundColor Yellow
}

Write-Host ("Backend working directory: {0}" -f (Get-Location)) -ForegroundColor DarkGray
Write-Host ""
Write-Host "Starting backend server on http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload


