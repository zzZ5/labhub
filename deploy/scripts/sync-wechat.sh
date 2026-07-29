#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

docker compose -f "$COMPOSE_FILE" exec -T backend python manage.py shell -c \
  "import json; from apps.wechat_articles.tasks import sync_all_wechat_accounts; results = sync_all_wechat_accounts(); print(json.dumps(results, ensure_ascii=False, default=str, indent=2))"
