#!/bin/bash
set -e

cd "$(dirname "$0")"

TEMPLATE_FILE="init/init.sql.template"
OUTPUT_FILE="init/init.sql"
ENV_FILE="../.env"

if [ ! -f "$ENV_FILE" ]; then
  echo " Missing .env file."
  exit 1
fi

echo " Generating $OUTPUT_FILE from $TEMPLATE_FILE using $ENV_FILE..."

# コメントと空行を除いて環境変数を読み込む（安全）
set -a
grep -v '^\s*#' "$ENV_FILE" | grep -v '^\s*$' > .env.tmp && source .env.tmp && rm .env.tmp
set +a

# 変数を展開して init.sql を生成
envsubst < "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo " $OUTPUT_FILE generated successfully at $OUTPUT_FILE"
