#!/bin/bash

set -e

# スクリプトの絶対パスを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
POSTGRES_DIR="$PROJECT_ROOT/docker/postgresql"

# OS別のsedコマンド設定
OS_TYPE=$(uname -s)
if [[ "$OS_TYPE" == "Darwin"* ]]; then
    # macOS用のsed（BSD版）
    SED_CMD="sed -i ''"
else
    # Linux用のsed（GNU版）
    SED_CMD="sed -i"
fi

cd "$POSTGRES_DIR"

TEMPLATE_FILE="init/init.sql.template"
OUTPUT_FILE="init/01-init.sql"
DEV_TEMPLATE_FILE="init/init-dev.sql.template"
DEV_OUTPUT_FILE="init/02-init-dev.sql"
ENV_FILE="$PROJECT_ROOT/.env"
MIGRATIONS_DIR="init/migrations"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing .env file at $ENV_FILE"
  exit 1
fi

echo "Generating $OUTPUT_FILE from $TEMPLATE_FILE using $ENV_FILE..."
echo "Generating $DEV_OUTPUT_FILE from $DEV_TEMPLATE_FILE using $ENV_FILE..."

# .envファイルの改行コードを変換（必要に応じて）
if command -v dos2unix >/dev/null 2>&1; then
  dos2unix "$ENV_FILE"
  $SED_CMD '1s/^\xEF\xBB\xBF//' "$ENV_FILE"
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
    $SED_CMD "s/\${$var}/${!var}/g" "$OUTPUT_FILE"
    $SED_CMD "s/\${$var}/${!var}/g" "$DEV_OUTPUT_FILE"
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
  done
fi