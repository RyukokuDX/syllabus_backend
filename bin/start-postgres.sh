#!/bin/bash

set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
POSTGRES_DIR="$PROJECT_ROOT/docker/postgresql"

# 1. Execute generate-init.sh
echo -e "\n1. Executing generate-init.sh..."
chmod +x "$SCRIPT_DIR/generate-init.sh"
"$SCRIPT_DIR/generate-init.sh"

# 2. Change to PostgreSQL directory
echo -e "\n2. Changing to PostgreSQL directory..."
cd "$POSTGRES_DIR" || exit

# 3. Start PostgreSQL with Docker Compose
echo -e "\n3. Starting PostgreSQL with Docker Compose..."
docker compose -f docker-compose.yml up -d postgres-db

# 4. Wait for container to start
echo -e "\n4. Waiting for container to start..."
sleep 10

echo -e "\nPostgreSQL is ready!" 