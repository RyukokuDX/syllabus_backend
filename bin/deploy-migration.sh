#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
POSTGRES_DIR="$PROJECT_ROOT/docker/postgresql"

# PostgreSQLディレクトリに移動
cd "$POSTGRES_DIR" || exit

# 環境変数ファイルからデータベース名を取得
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
else
    echo "Error: .env file not found in $PROJECT_ROOT"
    exit 1
fi

# マイグレーションディレクトリの確認
MIGRATIONS_DIR="$POSTGRES_DIR/migrations"
ARCHIVE_DIR="$POSTGRES_DIR/init/migrations"

if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "Error: migrationsディレクトリが見つかりません: $MIGRATIONS_DIR"
    exit 1
fi

if [ ! -d "$ARCHIVE_DIR" ]; then
    echo "init/migrationsディレクトリを作成します..."
    mkdir -p "$ARCHIVE_DIR"
fi

# SQLファイルを順に適用
SQL_FILES=$(find "$MIGRATIONS_DIR" -name "*.sql" | sort)
if [ -z "$SQL_FILES" ]; then
    echo "Error: migrationsディレクトリにSQLファイルが見つかりません: $MIGRATIONS_DIR"
    exit 1
fi

for file in $SQL_FILES; do
    filename=$(basename "$file")
    echo "適用中: $filename"
    
    # SQLファイルを適用（標準入力から）
    result=$(cat "$file" | docker-compose exec -T postgres-db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f - 2>&1)
    
    if [ $? -eq 0 ]; then
        echo "適用成功: $filename"
        mv "$file" "$ARCHIVE_DIR/$filename"
        echo "移動: $filename -> $ARCHIVE_DIR"
    else
        echo "エラー: $filename の適用に失敗しました"
        echo "psql出力: $result"
        exit 1
    fi
done

echo "全てのマイグレーションが完了しました。" 