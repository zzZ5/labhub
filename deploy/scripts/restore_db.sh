#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

if [ $# -ne 1 ]; then
  echo "Usage: bash deploy/scripts/restore_db.sh path/to/backup.sql"
  exit 1
fi

docker compose -f "$COMPOSE_FILE" exec -T db psql -U "${POSTGRES_USER:-labhub}" "${POSTGRES_DB:-labhub}" < "$1"
echo "Database restored from $1"
