#!/bin/bash

echo "Creating users..."
psql -U "$POSTGRES_USER" -d postgres -c "CREATE USER ${MASTER_USER} WITH PASSWORD '${MASTER_PASSWORD}';"
psql -U "$POSTGRES_USER" -d postgres -c "CREATE USER ${DEV_USER} WITH PASSWORD '${DEV_PASSWORD}';"
psql -U "$POSTGRES_USER" -d postgres -c "CREATE USER ${APP_USER} WITH PASSWORD '${APP_PASSWORD}';"

echo "Creating database..."
psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE ${MASTER_DB} OWNER ${MASTER_USER};"

echo "Granting privileges..."
psql -U "$POSTGRES_USER" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${MASTER_DB} TO ${MASTER_USER};"
psql -U "$POSTGRES_USER" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${MASTER_DB} TO ${DEV_USER};"
psql -U "$POSTGRES_USER" -d postgres -c "GRANT CONNECT ON DATABASE ${MASTER_DB} TO ${APP_USER};"

echo "Creating tables..."
psql -U "$POSTGRES_USER" -d ${MASTER_DB} -f /docker-entrypoint-initdb.d/02-init.sql

echo "Starting custom migrations..."
for f in /docker-entrypoint-initdb.d/migrations/*.sql; do
  echo "Running migration: $f"
  psql -U "$POSTGRES_USER" -d ${MASTER_DB} -f "$f"
done 