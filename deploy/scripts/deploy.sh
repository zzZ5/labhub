#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

git pull
docker compose -f "$COMPOSE_FILE" build
docker compose -f "$COMPOSE_FILE" up -d db redis
docker compose -f "$COMPOSE_FILE" up -d frontend backend
docker compose -f "$COMPOSE_FILE" exec -T backend python manage.py migrate
docker compose -f "$COMPOSE_FILE" exec -T backend python manage.py collectstatic --noinput
docker compose -f "$COMPOSE_FILE" up -d celery_worker celery_beat nginx
docker compose -f "$COMPOSE_FILE" ps
