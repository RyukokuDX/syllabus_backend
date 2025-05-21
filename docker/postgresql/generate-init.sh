#!/bin/bash

set -e

cd "$(dirname "$0")"

TEMPLATE_FILE="init/init.sql.template"
OUTPUT_FILE="init/init.sql"
ENV_FILE="../.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing .env file."
  exit 1
fi

echo "Generating $OUTPUT_FILE from $TEMPLATE_FILE using $ENV_FILE..."

# .envファイルの改行コードを変換（必要に応じて）
if command -v dos2unix >/dev/null 2>&1; then
  dos2unix "$ENV_FILE"
  sed -i '1s/^\xEF\xBB\xBF//' "$ENV_FILE"
fi

# 環境変数を読み込む
while IFS= read -r line || [ -n "$line" ]; do
  # コメントと空行をスキップ
  [[ $line =~ ^#.*$ ]] && continue
  [[ -z $line ]] && continue
  
  # 変数名と値を分離して設定
  if [[ $line =~ ^([A-Z][A-Z0-9_]*)=(.*)$ ]]; then
    export "${BASH_REMATCH[1]}"="${BASH_REMATCH[2]}"
  fi
done < "$ENV_FILE"

# テンプレート変換
envsubst < "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo "$OUTPUT_FILE generated successfully at $OUTPUT_FILE"
