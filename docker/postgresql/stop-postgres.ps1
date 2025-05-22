# Character encoding settings
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# PostgreSQL Stop and Volume Cleanup Script

# 0. Change to target directory
Write-Host "0. Changing to target directory..."
$workspacePath = Join-Path $env:USERPROFILE "Documents\github\syllabus_backend"
Set-Location (Join-Path $workspacePath "docker\postgresql")

# 1. Stop PostgreSQL with Docker Compose
Write-Host "`n1. Stopping PostgreSQL with Docker Compose..."
docker-compose down

# 2. Remove volume
Write-Host "`n2. Removing volume..."
$volumeExists = docker volume ls -q | Select-String -Pattern "postgres-data"
if ($volumeExists) {
    docker volume rm postgres-data
    Write-Host "Volume removed successfully"
} else {
    Write-Host "Volume does not exist"
} 