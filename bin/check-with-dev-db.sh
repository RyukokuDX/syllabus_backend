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

# 最新のマイグレーションファイルを取得
LATEST_MIGRATION=$(ls -t "$POSTGRES_DIR/migrations_dev"/*.sql | head -n1)
if [ -z "$LATEST_MIGRATION" ]; then
    echo "マイグレーションファイルが見つかりません"
    exit 1
fi

MIGRATION_NAME=$(basename "$LATEST_MIGRATION")
echo "最新のマイグレーションファイル: $MIGRATION_NAME を適用します..."

# ファイルの存在確認
if [ ! -f "$LATEST_MIGRATION" ]; then
    echo "エラー: マイグレーションファイルが見つかりません: $LATEST_MIGRATION"
    exit 1
fi

echo "ファイルパス: $LATEST_MIGRATION"

# ファイルの内容を直接コンテナ内で実行
echo "マイグレーションを適用中..."
docker-compose exec -T postgres-db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 < "$LATEST_MIGRATION"
MIGRATION_EXIT_CODE=$?

# 結果の確認
if [ $MIGRATION_EXIT_CODE -eq 0 ]; then
    echo "マイグレーションが正常に適用されました"
    
    # マイグレーションファイルをmigrationsディレクトリに移動
    echo "マイグレーションファイルをmigrationsディレクトリに移動します..."
    mv "$LATEST_MIGRATION" "$POSTGRES_DIR/migrations/"
else
    echo "エラー: マイグレーションの実行に失敗しました"
    echo "マイグレーションファイルはmigrations_devディレクトリに残されています"
    exit 1
fi 