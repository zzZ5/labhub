# LabHub

LabHub is a Django + Vue portal and internal research management platform for laboratory groups. This first stage provides the runnable foundation: backend, frontend, PostgreSQL, Redis, Celery, Nginx, Docker Compose, and `/api/health/`.

## Architecture

- `backend/`: Django project, REST framework, Celery, environment-based settings.
- `frontend/`: Vue 3, TypeScript, Vite, Pinia, Vue Router, Element Plus.
- `deploy/nginx/`: reverse proxy, frontend hosting, static and media handling.
- `deploy/scripts/`: initialization, deployment, backup, and restore helpers.

## Development

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/api/health/
- Django admin: http://localhost:8000/admin/

## Production

```bash
cp .env.production.example .env
# edit .env before production use
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

Or run:

```bash
bash deploy/scripts/init.sh
```

For a simple GitHub-based server deployment, see `docs/github-deploy.md`.

## Common Commands

```bash
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f celery_worker
bash deploy/scripts/deploy.sh
bash deploy/scripts/backup_db.sh
bash deploy/scripts/backup_media.sh
```

## Docker Hub Network Troubleshooting

If Docker fails at `failed to fetch oauth token` or cannot reach `auth.docker.io`, the project files are usually fine. The host cannot reach Docker Hub reliably.

Try:

```bash
docker pull python:3.14-slim
docker pull node:22-alpine
docker pull postgres:17-alpine
docker pull redis:7-alpine
docker compose up --build
```

If the pull still fails, configure Docker Desktop with a working proxy or registry mirror, then restart Docker Desktop. On some networks, disabling IPv6 or changing DNS to `1.1.1.1` / `8.8.8.8` also fixes misrouted `auth.docker.io` requests.

If images were built previously, you can start without rebuilding:

```bash
docker compose up -d --no-build
```

## Notes

- Public media is served by Nginx from `/media/`.
- Production Nginx exposes host port `8088` by default. Change `NGINX_HTTP_PORT` in `.env` if needed.
- Sensitive internal files must be stored under `protected_media` and downloaded through authenticated Django APIs in later phases.
- Do not commit `.env`.
- HTTPS certificates can be mounted under `deploy/ssl/`; see `deploy/ssl/README.md`.
