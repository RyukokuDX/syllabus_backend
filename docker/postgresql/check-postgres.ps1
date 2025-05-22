# Character encoding settings
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# PostgreSQL Status Check Script

# 0. Change to target directory
Write-Host "0. Changing to target directory..."
$workspacePath = Join-Path $env:USERPROFILE "Documents\github\syllabus_backend"
Set-Location (Join-Path $workspacePath "docker\postgresql")

# 1. Check container status
Write-Host "`n1. Checking container status..."
$containerStatus = docker ps --filter "name=postgres-db" --format "{{.Status}}"
if ($containerStatus) {
    Write-Host "Container is running: $containerStatus"
} else {
    Write-Host "Container is not running"
    exit
}

# 2. Display table entry counts
Write-Host "`n2. Displaying table entry counts..."

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