param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 8501
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "Starting CyberSentinel services..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$root'; python -m uvicorn backend.app:app --host 127.0.0.1 --port $BackendPort --reload`"" -WindowStyle Normal | Out-Null
Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$root'; python -m streamlit run frontend/app.py --server.port $FrontendPort --server.headless true`"" -WindowStyle Normal | Out-Null
Start-Sleep -Seconds 3

Start-Process "http://localhost:$FrontendPort" | Out-Null

Write-Host "Backend: http://127.0.0.1:$BackendPort" -ForegroundColor Green
Write-Host "Frontend: http://localhost:$FrontendPort" -ForegroundColor Green
Write-Host "Browser opened to dashboard." -ForegroundColor Green
