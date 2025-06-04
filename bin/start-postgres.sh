#!/bin/bash

set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
POSTGRES_DIR="$PROJECT_ROOT/docker/postgresql"

echo "0. Changing to target directory..."
cd "$POSTGRES_DIR" || exit

# 1. Execute generate-init.sh
echo -e "\n1. Executing generate-init.sh..."
cd "$POSTGRES_DIR" || exit
chmod +x generate-init.sh
./generate-init.sh

# 2. Start PostgreSQL with Docker Compose
echo -e "\n2. Starting PostgreSQL with Docker Compose..."
docker-compose up -d

# 3. Wait for container to start
echo -e "\n3. Waiting for container to start..."
sleep 10

echo -e "\nPostgreSQL is ready!" 