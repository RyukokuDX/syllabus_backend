#!/bin/bash

set -e

# スクリプトの絶対パスを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

TEMPLATE_FILE="init/init.sql.template"
OUTPUT_FILE="init/01-init.sql"
DEV_TEMPLATE_FILE="init/init-dev.sql.template"
DEV_OUTPUT_FILE="init/02-init-dev.sql"
MIGRATIONS_DIR="init/migrations"
DOCKER_MIGRATIONS_DIR="init/docker-entrypoint-initdb.d/migrations"

# マイグレーションディレクトリの作成
mkdir -p "$DOCKER_MIGRATIONS_DIR"

echo "Generating $OUTPUT_FILE from $TEMPLATE_FILE..."
echo "Generating $DEV_OUTPUT_FILE from $DEV_TEMPLATE_FILE..."

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

# マイグレーションファイルの自動挿入とコピー
if [ -d "$MIGRATIONS_DIR" ]; then
  echo "MIGRATIONS_DIR: $MIGRATIONS_DIR"
  for sqlfile in "$MIGRATIONS_DIR"/*.sql; do
    [ -e "$sqlfile" ] || { echo "No .sql files found in $MIGRATIONS_DIR"; continue; }
    filename=$(basename "$sqlfile")
    echo "Adding migration: $filename"
    # マイグレーションファイルをコピー
    cp "$sqlfile" "$DOCKER_MIGRATIONS_DIR/"
    echo "\\i /docker-entrypoint-initdb.d/migrations/$filename" >> "$OUTPUT_FILE"
    echo "\\i /docker-entrypoint-initdb.d/migrations/$filename" >> "$DEV_OUTPUT_FILE"
  done
fi

# 開発用データベースの初期化コマンドを追加
echo "
-- ========== 開発用データベースの初期化 ==========

\\i /docker-entrypoint-initdb.d/02-init-dev.sql" >> "$OUTPUT_FILE"
