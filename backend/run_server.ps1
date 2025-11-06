#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the AdultingOS FastAPI server.

.DESCRIPTION
    This script starts the FastAPI backend server on http://127.0.0.1:8001.
    It handles the correct working directory and cleans up any existing processes on port 8001.

.EXAMPLE
    .\run_server.ps1
#>

# Change to the backend directory (where main.py is located)
$BackendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BackendDir

Write-Host "Starting AdultingOS FastAPI Server..." -ForegroundColor Cyan
Write-Host "Location: $BackendDir" -ForegroundColor Gray
Write-Host ""

# Check if port 8001 is already in use
$PortInUse = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue

if ($PortInUse) {
    Write-Host "WARNING: Port 8001 is already in use. Attempting to free it..." -ForegroundColor Yellow
    $ProcessIds = $PortInUse | Select-Object -ExpandProperty OwningProcess -Unique
    
    foreach ($ProcessId in $ProcessIds) {
        try {
            Stop-Process -Id $ProcessId -Force -ErrorAction Stop
            Write-Host "Stopped process $ProcessId" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to stop process $ProcessId" -ForegroundColor Red
        }
    }
    
    # Wait a moment for the port to be released
    Start-Sleep -Seconds 1
}

# Start the uvicorn server
Write-Host ""
Write-Host "Starting FastAPI server on http://127.0.0.1:8001" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Note: --reload is disabled by default as it can cause issues with file watchers
# To enable auto-reload during development, uncomment the line below and comment out the other uvicorn line
# uvicorn main:app --host 127.0.0.1 --port 8001 --reload
uvicorn main:app --host 127.0.0.1 --port 8001
