#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
BACKUP_DIR="${BACKUP_DIR:-backups/db}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
docker compose -f "$COMPOSE_FILE" exec -T db pg_dump -U "${POSTGRES_USER:-labhub}" "${POSTGRES_DB:-labhub}" > "$BACKUP_DIR/labhub_${TIMESTAMP}.sql"
echo "Database backup written to $BACKUP_DIR/labhub_${TIMESTAMP}.sql"
