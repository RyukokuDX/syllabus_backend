#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# PostgreSQLの停止
cd "$PROJECT_ROOT/docker/postgresql" || exit
docker-compose down

echo "PostgreSQL has been stopped." 