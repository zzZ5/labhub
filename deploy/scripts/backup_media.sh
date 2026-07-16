#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
BACKUP_DIR="${BACKUP_DIR:-backups/media}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/labhub_media_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

BACKEND_CONTAINER="$(docker compose -f "$COMPOSE_FILE" ps -q backend)"
if [ -z "$BACKEND_CONTAINER" ] || ! docker inspect -f '{{.State.Running}}' "$BACKEND_CONTAINER" 2>/dev/null | grep -q true; then
  echo "Backend container is not running; media volumes were not backed up." >&2
  exit 1
fi

docker compose -f "$COMPOSE_FILE" exec -T backend tar -czf - -C /app media protected_media > "$BACKUP_FILE"

if [ ! -s "$BACKUP_FILE" ]; then
  echo "Media backup is empty: $BACKUP_FILE" >&2
  exit 1
fi

echo "Media backup written to $BACKUP_FILE"
