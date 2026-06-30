#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

if [ ! -f .env ]; then
  echo ".env not found. Copying .env.example to .env."
  cp .env.example .env
  echo "Edit .env before using this script in production."
fi

docker compose -f "$COMPOSE_FILE" build
docker compose -f "$COMPOSE_FILE" up -d db redis

echo "Waiting for database..."
until docker compose -f "$COMPOSE_FILE" exec -T db pg_isready -U "${POSTGRES_USER:-labhub}" -d "${POSTGRES_DB:-labhub}"; do
  sleep 2
done

docker compose -f "$COMPOSE_FILE" up -d backend
docker compose -f "$COMPOSE_FILE" exec backend python manage.py migrate
docker compose -f "$COMPOSE_FILE" exec backend python manage.py collectstatic --noinput

if [ -n "${ADMIN_EMAIL:-}" ] && [ -n "${ADMIN_PASSWORD:-}" ]; then
  docker compose -f "$COMPOSE_FILE" exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); User.objects.filter(email='$ADMIN_EMAIL').exists() or User.objects.create_superuser(username='$ADMIN_EMAIL', email='$ADMIN_EMAIL', password='$ADMIN_PASSWORD')"
fi

docker compose -f "$COMPOSE_FILE" up -d
docker compose -f "$COMPOSE_FILE" ps
