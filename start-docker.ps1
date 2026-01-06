# CyberSentinel - Docker Startup Script
# This script checks Docker status and provides commands to start the project

Write-Host "=== CyberSentinel Docker Startup ===" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker Desktop status..." -ForegroundColor Yellow
try {
    $dockerVersion = docker version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker is running!" -ForegroundColor Green
        Write-Host ""
        
        # Navigate to project directory
        $projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
        Set-Location $projectPath
        
        Write-Host "Starting CyberSentinel services..." -ForegroundColor Yellow
        Write-Host ""
        
        # Start docker-compose
        docker-compose up --build
    }
    else {
        throw "Docker not responding"
    }
}
catch {
    Write-Host "✗ Docker Desktop is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Docker Desktop first. Options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1: Start Docker Desktop from Start Menu" -ForegroundColor Cyan
    Write-Host "  - Search for 'Docker Desktop' and launch it"
    Write-Host "  - Wait for it to fully start (whale icon in system tray)"
    Write-Host ""
    Write-Host "Option 2: Start Docker Desktop via PowerShell (if installed in default location):" -ForegroundColor Cyan
    Write-Host "  Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 3: Start Docker service manually:" -ForegroundColor Cyan
    Write-Host "  Start-Service docker" -ForegroundColor White
    Write-Host ""
    Write-Host "After Docker Desktop starts, run this script again or run:" -ForegroundColor Yellow
    Write-Host "  docker-compose up --build" -ForegroundColor White
    Write-Host ""
    
    # Ask if user wants to try starting Docker Desktop
    $response = Read-Host "Would you like to try starting Docker Desktop now? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Attempting to start Docker Desktop..." -ForegroundColor Yellow
        
        # Try common Docker Desktop paths
        $dockerPaths = @(
            "C:\Program Files\Docker\Docker\Docker Desktop.exe",
            "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe",
            "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe",
            "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe"
        )
        
        $found = $false
        foreach ($path in $dockerPaths) {
            if (Test-Path $path) {
                Write-Host "Found Docker Desktop at: $path" -ForegroundColor Green
                Start-Process $path
                $found = $true
                break
            }
        }
        
        if (-not $found) {
            Write-Host "Could not find Docker Desktop. Please start it manually." -ForegroundColor Red
        }
        else {
            Write-Host ""
            Write-Host "Docker Desktop is starting. Please wait 30-60 seconds for it to fully initialize," -ForegroundColor Yellow
            Write-Host "then run: docker-compose up --build" -ForegroundColor White
        }
    }
    
    exit 1
}

