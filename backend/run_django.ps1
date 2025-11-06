.\backend\run_server.ps1#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the AdultingOS Django server.

.DESCRIPTION
    This script starts the Django REST API server on http://127.0.0.1:8000.
    It handles the correct working directory and cleans up any existing processes on port 8000.

.EXAMPLE
    .\run_django.ps1
#>

# Change to the Django project directory (where manage.py is located)
$DjangoDir = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "adultingos_web"
Set-Location $DjangoDir

Write-Host "Starting AdultingOS Django Server..." -ForegroundColor Cyan
Write-Host "Location: $DjangoDir" -ForegroundColor Gray
Write-Host ""

# Check if port 8000 is already in use
$PortInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($PortInUse) {
    Write-Host "WARNING: Port 8000 is already in use. Attempting to free it..." -ForegroundColor Yellow
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

# Check for unapplied migrations
Write-Host "Checking for unapplied migrations..." -ForegroundColor Gray
$MigrationCheck = python manage.py showmigrations --plan | Select-String "[ ]"

if ($MigrationCheck) {
    Write-Host "WARNING: You have unapplied migrations!" -ForegroundColor Yellow
    Write-Host "Run 'python manage.py migrate' to apply them." -ForegroundColor Yellow
    Write-Host ""
}

# Start the Django development server
Write-Host "Starting Django server on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Admin interface: http://127.0.0.1:8000/admin" -ForegroundColor Gray
Write-Host "Browsable API: http://127.0.0.1:8000/api" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python manage.py runserver 127.0.0.1:8000
