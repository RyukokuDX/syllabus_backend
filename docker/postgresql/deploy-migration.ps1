# PostgreSQLコンテナが実行中か確認
$containerName = "postgres-db"
$containerStatus = docker ps -f "name=$containerName" --format "{{.Status}}"

if (-not $containerStatus) {
    Write-Host "Error: PostgreSQLコンテナが実行されていません。"
    exit 1
}

# 環境変数からDB名とユーザー名を取得
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path (Split-Path -Parent $scriptPath) ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "Error: .envファイルが見つかりません: $envFile"
    exit 1
}

$envContent = Get-Content $envFile -Encoding UTF8
$dbName = ($envContent | Where-Object { $_ -match "POSTGRES_DB=" }) -replace "POSTGRES_DB=", ""
$userName = ($envContent | Where-Object { $_ -match "POSTGRES_USER=" }) -replace "POSTGRES_USER=", ""

if ([string]::IsNullOrEmpty($dbName) -or [string]::IsNullOrEmpty($userName)) {
    Write-Host "Error: .envファイルからPOSTGRES_DBまたはPOSTGRES_USERの設定が見つかりません。"
    exit 1
}

# マイグレーションディレクトリの確認
$migrationsDir = Join-Path $scriptPath "migrations"
$archiveDir = Join-Path $scriptPath "init\migrations"

if (-not (Test-Path $migrationsDir)) {
    Write-Host "Error: migrationsディレクトリが見つかりません: $migrationsDir"
    exit 1
}

if (-not (Test-Path $archiveDir)) {
    Write-Host "init/migrationsディレクトリを作成します..."
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
}

# SQLファイルを順に適用
$sqlFiles = Get-ChildItem -Path $migrationsDir -Filter "*.sql" | Sort-Object Name
if ($sqlFiles.Count -eq 0) {
    Write-Host "Error: migrationsディレクトリにSQLファイルが見つかりません: $migrationsDir"
    exit 1
}

foreach ($file in $sqlFiles) {
    Write-Host "適用中: $($file.Name)"
    $sqlContent = Get-Content $file.FullName -Encoding UTF8 | Out-String
    $result = $sqlContent | docker exec -i $containerName psql -U $userName -d $dbName -f -
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "適用成功: $($file.Name)"
        Move-Item -Path $file.FullName -Destination (Join-Path $archiveDir $file.Name) -Force
        Write-Host "移動: $($file.Name) -> $archiveDir"
    } else {
        Write-Host "エラー: $($file.Name) の適用に失敗しました"
        Write-Host "psql出力: $result"
        exit 1
    }
}

Write-Host "全てのマイグレーションが完了しました。" 