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

# マイグレーションファイルのコピー
echo "マイグレーションファイルをコピーします..."
cp "$POSTGRES_DIR/migrations_dev"/*.sql "$POSTGRES_DIR/migrations/"

# マイグレーションの適用
echo "マイグレーションを適用します..."
docker-compose exec -T postgres-db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "/docker-entrypoint-initdb.d/migrations/$(basename "$(ls -t migrations/*.sql | head -n1)")"

# 結果の確認
if [ $? -eq 0 ]; then
    echo "マイグレーションが正常に適用されました"
    
    # テーブル数の確認
    echo "テーブル数を確認します..."
    docker-compose exec -T postgres-db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    SELECT table_name, count(*) 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    GROUP BY table_name 
    ORDER BY table_name;"
else
    echo "エラー: マイグレーションの実行に失敗しました"
    exit 1
fi 