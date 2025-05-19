#!/bin/bash
echo "Starting custom migrations..."
for f in /docker-entrypoint-initdb.d/02-migrations/*.sql; do
  echo "Running migration: $f"
  psql -U "$POSTGRES_USER" -d master_db -f "$f"
done
