#!/bin/bash

set -e

cd "$(dirname "$0")"

TEMPLATE_FILE="init/init.sql.template"
OUTPUT_FILE="init/01-init.sql"
DEV_TEMPLATE_FILE="init/init-dev.sql.template"
DEV_OUTPUT_FILE="init/02-init-dev.sql"
ENV_FILE="../.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing .env file at $ENV_FILE"
  exit 1
fi

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
for var in POSTGRES_DB DEV_USER DEV_PASSWORD APP_USER APP_PASSWORD; do
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
MIGRATIONS_DIR="init/migrations"
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

# 開発用データベースの初期化コマンドを追加
echo "
-- ========== 開発用データベースの初期化 ==========

\\i /docker-entrypoint-initdb.d/02-init-dev.sql" >> "$OUTPUT_FILE"
