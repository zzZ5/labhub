#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

git pull
docker compose -f "$COMPOSE_FILE" build
docker compose -f "$COMPOSE_FILE" up -d
docker compose -f "$COMPOSE_FILE" exec backend python manage.py migrate
docker compose -f "$COMPOSE_FILE" exec backend python manage.py collectstatic --noinput
docker compose -f "$COMPOSE_FILE" restart backend celery_worker celery_beat nginx
docker compose -f "$COMPOSE_FILE" ps
