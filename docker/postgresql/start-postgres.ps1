# Character encoding settings
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# PostgreSQL Startup and Initialization Script

# 0. Change to target directory
Write-Host "0. Changing to target directory..."
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 1. Execute generate-init.sh in WSL
Write-Host "`n1. Executing generate-init.sh in WSL..."
$wslPath = wsl wslpath -a $scriptPath
wsl bash -c "cd '$wslPath' && dos2unix generate-init.sh && chmod +x generate-init.sh && ./generate-init.sh"

# 2. Start PostgreSQL with Docker Compose
Write-Host "`n2. Starting PostgreSQL with Docker Compose..."
docker-compose up -d

# 3. Wait for container to start
Write-Host "`n3. Waiting for container to start..."
Start-Sleep -Seconds 10

# 4. Display table entry counts
Write-Host "`n4. Displaying table entry counts..."

# Get list of tables first
$tablesQuery = @"
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
"@

$tables = docker exec postgres-db psql -U postgres -d syllabus_db -t -c "$tablesQuery"

# For each table, get the record count
foreach ($table in $tables) {
    $table = $table.Trim()
    if ($table) {
        $countQuery = "SELECT COUNT(*) FROM $table;"
        $count = docker exec postgres-db psql -U postgres -d syllabus_db -t -c "$countQuery"
        Write-Host "Table: $table - Records: $($count.Trim())"
    }
} 