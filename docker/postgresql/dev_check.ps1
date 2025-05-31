# データベース接続情報
$DB_NAME = "develop_table"
$DB_USER = "postgres"
$DB_PASSWORD = "postgres"
$DB_HOST = "localhost"
$DB_PORT = "5432"

# マイグレーションファイルのディレクトリ
$MIGRATION_DIR = "init/migrations"

# データベースに接続してSQLを実行する関数
function Execute-Sql {
    param (
        [string]$sql
    )
    $env:PGPASSWORD = $DB_PASSWORD
    $result = psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c $sql 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error executing SQL: $result" -ForegroundColor Red
        exit 1
    }
    Write-Host $result
}

# マイグレーションファイルを実行する関数
function Execute-Migration {
    param (
        [string]$file
    )
    Write-Host "Executing migration: $file" -ForegroundColor Yellow
    $sql = Get-Content $file -Raw
    Execute-Sql $sql
}

# メイン処理
try {
    # マイグレーションファイルの存在確認
    if (-not (Test-Path $MIGRATION_DIR)) {
        Write-Host "Migration directory not found: $MIGRATION_DIR" -ForegroundColor Red
        exit 1
    }

    # マイグレーションファイルを取得して実行
    $migrationFiles = Get-ChildItem -Path $MIGRATION_DIR -Filter "*.sql" | Sort-Object Name
    foreach ($file in $migrationFiles) {
        Execute-Migration $file.FullName
    }

    Write-Host "All migrations completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
finally {
    # 環境変数のクリーンアップ
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
} 