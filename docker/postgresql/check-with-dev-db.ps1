# PostgreSQLコンテナが実行中か確認
$containerName = "postgres-db"
$containerStatus = docker ps -f "name=$containerName" --format "{{.Status}}"

if (-not $containerStatus) {
    Write-Host "Error: PostgreSQLコンテナが実行されていません。"
    exit 1
}

# 環境変数から開発用DB名を取得
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $scriptPath ".env"
$envContent = Get-Content $envFile
$devDbName = ($envContent | Where-Object { $_ -match "DEV_DB=" }) -replace "DEV_DB=", ""

if ([string]::IsNullOrEmpty($devDbName)) {
    Write-Host "Error: .envファイルからDEV_DBの設定が見つかりません。"
    exit 1
}

# 最新のマイグレーションファイルを取得
$migrationsDir = Join-Path $scriptPath "init/migrations"
$latestMigration = Get-ChildItem -Path $migrationsDir -Filter "*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($null -eq $latestMigration) {
    Write-Host "Error: マイグレーションファイルが見つかりません。"
    exit 1
}

Write-Host "最新のマイグレーションファイル: $($latestMigration.Name) を適用します..."

# マイグレーションを実行
$migrationContent = Get-Content $latestMigration.FullName -Raw
# $migrationContent = $migrationContent -replace "syllabus", $devDbName

# 一時ファイルに書き出し
$tempFile = [System.IO.Path]::GetTempFileName()
$migrationContent | Out-File -FilePath $tempFile -Encoding UTF8

# マイグレーションを実行
Get-Content $tempFile | docker exec -i postgres-db psql -U dev_user -d $devDbName

# 一時ファイルを削除
Remove-Item $tempFile