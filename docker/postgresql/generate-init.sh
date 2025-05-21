#!/bin/bash

set -e

cd "$(dirname "$0")"

TEMPLATE_FILE="init/init.sql.template"
OUTPUT_FILE="init/01-init.sql"
ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing .env file at $ENV_FILE"
  exit 1
fi

echo "Generating $OUTPUT_FILE from $TEMPLATE_FILE using $ENV_FILE..."

# .envファイルの改行コードを変換（必要に応じて）
if command -v dos2unix >/dev/null 2>&1; then
  dos2unix "$ENV_FILE"
  sed -i '1s/^\xEF\xBB\xBF//' "$ENV_FILE"
fi

# 環境変数を読み込む
export $(grep -v '^#' "$ENV_FILE" | xargs)

# テンプレート変換
cp "$TEMPLATE_FILE" "$OUTPUT_FILE"

# 環境変数を置換
for var in MASTER_USER MASTER_PASSWORD MASTER_DB DEV_USER DEV_PASSWORD DEV_DB APP_USER APP_PASSWORD; do
  if [ -n "${!var}" ]; then
    sed -i "s/\${$var}/${!var}/g" "$OUTPUT_FILE"
  else
    echo "Warning: $var is not set"
  fi
done

echo "$OUTPUT_FILE generated successfully at $OUTPUT_FILE"
