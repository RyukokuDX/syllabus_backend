#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 0. Change to target directory
echo "0. Changing to target directory..."
cd "$PROJECT_ROOT/docker/postgresql" || exit

# 1. Stop PostgreSQL with Docker Compose
echo -e "\n1. Stopping PostgreSQL with Docker Compose..."
docker-compose down

# 2. Remove volume
echo -e "\n2. Removing volume..."
if docker volume ls -q | grep -q "postgres-data"; then
    docker volume rm postgres-data
    echo "Volume removed successfully"
else
    echo "Volume does not exist"
fi

echo "PostgreSQL has been stopped." 