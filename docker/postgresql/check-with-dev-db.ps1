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
if (-not (Test-Path $envFile)) {
    Write-Host "Error: .envファイルが見つかりません: $envFile"
    exit 1
}

$envContent = Get-Content $envFile -Encoding UTF8
$devDbName = ($envContent | Where-Object { $_ -match "DEV_DB=" }) -replace "DEV_DB=", ""

if ([string]::IsNullOrEmpty($devDbName)) {
    Write-Host "Error: .envファイルからDEV_DBの設定が見つかりません。"
    exit 1
}

# マイグレーションディレクトリの確認と作成
$migrationsDevDir = Join-Path $scriptPath "migrations_dev"
$migrationsDir = Join-Path $scriptPath "migrations"

if (-not (Test-Path $migrationsDevDir)) {
    Write-Host "migrations_devディレクトリを作成します..."
    New-Item -ItemType Directory -Path $migrationsDevDir -Force | Out-Null
}

if (-not (Test-Path $migrationsDir)) {
    Write-Host "migrationsディレクトリを作成します..."
    New-Item -ItemType Directory -Path $migrationsDir -Force | Out-Null
}

# 最新のマイグレーションファイルを取得
$latestMigration = Get-ChildItem -Path $migrationsDevDir -Filter "*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($null -eq $latestMigration) {
    Write-Host "Error: migrations_devディレクトリにSQLファイルが見つかりません: $migrationsDevDir"
    exit 1
}

Write-Host "最新のマイグレーションファイル: $($latestMigration.Name) を適用します..."

# 登録予定の件数を取得（行頭が ( で始まる行をカウント）
$fileContent = Get-Content $latestMigration.FullName -Encoding UTF8
$valueLines = ($fileContent | Where-Object { $_.TrimStart().StartsWith("(") }).Count
if ($valueLines -eq 0) {
    Write-Host "エラー: マイグレーションファイルにVALUES行が見つかりません: $($latestMigration.FullName)"
    exit 1
}
$expectedCount = $valueLines

if (-not $expectedCount) {
    Write-Host "エラー: 登録予定の件数が取得できません"
    exit 1
}

# マイグレーションを実行
$sqlContent = Get-Content $latestMigration.FullName -Encoding UTF8 | Out-String
$result = $sqlContent | docker exec -i $containerName psql -U postgres -d $devDbName -f -

if ($LASTEXITCODE -ne 0) {
    Write-Host "エラー: マイグレーションの実行に失敗しました"
    exit 1
}

# 実際の登録件数を取得
if ([string]::IsNullOrEmpty($result)) {
    Write-Host "エラー: マイグレーションの実行結果が空です"
    exit 1
}

$resultMatches = [regex]::Matches($result, "INSERT 0 (\d+)")
if ($resultMatches.Count -eq 0) {
    Write-Host "エラー: マイグレーション実行結果にINSERT文が見つかりません"
    Write-Host "実行結果: $result"
    exit 1
}
$actualCount = $resultMatches[0].Groups[1].Value

if (-not $actualCount) {
    Write-Host "エラー: 登録された件数が取得できません"
    exit 1
}

# 登録件数を比較
if ($expectedCount -eq $actualCount) {
    Write-Host "登録件数が一致しました（$actualCount件）"
    
    # migrationsディレクトリに移動
    $destinationPath = Join-Path $migrationsDir $latestMigration.Name
    Move-Item -Path $latestMigration.FullName -Destination $destinationPath -Force
    Write-Host "マイグレーションファイルを $migrationsDir に移動しました"
} else {
    Write-Host "エラー: 登録件数が一致しません"
    Write-Host "予定: $expectedCount件"
    Write-Host "実際: $actualCount件"
    exit 1
}