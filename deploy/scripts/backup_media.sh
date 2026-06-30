#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-backups/media}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/labhub_media_${TIMESTAMP}.tar.gz" media protected_media 2>/dev/null || true
echo "Media backup written to $BACKUP_DIR/labhub_media_${TIMESTAMP}.tar.gz"
