#!/bin/bash

set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
POSTGRES_DIR="$PROJECT_ROOT/docker/postgresql"

echo "0. Changing to target directory..."
cd "$POSTGRES_DIR" || exit

# 初期化ファイルの生成
echo -e "\n1. Generating initialization files..."

# 環境変数ファイルの確認
ENV_FILE="$PROJECT_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Missing .env file at $ENV_FILE"
  exit 1
fi

# テンプレートファイルのパス
TEMPLATE_FILE="init/init.sql.template"
OUTPUT_FILE="init/01-init.sql"
DEV_TEMPLATE_FILE="init/init-dev.sql.template"
DEV_OUTPUT_FILE="init/02-init-dev.sql"
MIGRATIONS_DIR="init/migrations"

echo "Generating $OUTPUT_FILE from $TEMPLATE_FILE using $ENV_FILE..."
echo "Generating $DEV_OUTPUT_FILE from $DEV_TEMPLATE_FILE using $ENV_FILE..."

# .envファイルの改行コードを変換（必要に応じて）
if command -v dos2unix >/dev/null 2>&1; then
  dos2unix "$ENV_FILE"
  sed -i '1s/^\xEF\xBB\xBF//' "$ENV_FILE"
fi

# 環境変数を読み込む
set -a
. "$ENV_FILE"
set +a

# テンプレート変換
cp "$TEMPLATE_FILE" "$OUTPUT_FILE"
cp "$DEV_TEMPLATE_FILE" "$DEV_OUTPUT_FILE"

# 環境変数を置換
for var in POSTGRES_DB DEV_DB DEV_USER DEV_PASSWORD APP_USER APP_PASSWORD; do
  if [ -n "${!var}" ]; then
    sed -i "s/\${$var}/${!var}/g" "$OUTPUT_FILE"
    sed -i "s/\${$var}/${!var}/g" "$DEV_OUTPUT_FILE"
  else
    echo "Warning: $var is not set"
  fi
done

echo "$OUTPUT_FILE generated successfully"
echo "$DEV_OUTPUT_FILE generated successfully"

# マイグレーションファイルの自動挿入
if [ -d "$MIGRATIONS_DIR" ]; then
  echo "MIGRATIONS_DIR: $MIGRATIONS_DIR"
  for sqlfile in "$MIGRATIONS_DIR"/*.sql; do
    [ -e "$sqlfile" ] || { echo "No .sql files found in $MIGRATIONS_DIR"; continue; }
    filename=$(basename "$sqlfile")
    echo "Adding migration: $filename"
    echo "\\i /docker-entrypoint-initdb.d/migrations/$filename" >> "$OUTPUT_FILE"
    echo "\\i /docker-entrypoint-initdb.d/migrations/$filename" >> "$DEV_OUTPUT_FILE"
  done
fi

# PostgreSQLの起動
echo -e "\n2. Starting PostgreSQL with Docker Compose..."
docker-compose up -d

echo -e "\n3. Waiting for container to start..."
sleep 10

echo -e "\n4. Displaying table entry counts..."

# Get list of tables first
tables=$(docker exec postgres-db psql -U postgres -d syllabus_db -t -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;")

# For each table, get the record count
while IFS= read -r table; do
    table=$(echo "$table" | tr -d '[:space:]')
    if [ -n "$table" ]; then
        count=$(docker exec postgres-db psql -U postgres -d syllabus_db -t -c "SELECT COUNT(*) FROM $table;")
        echo "Table: $table - Records: $(echo "$count" | tr -d '[:space:]')"
    fi
done <<< "$tables"

echo -e "\nPostgreSQL is ready!" 