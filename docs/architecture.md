# LabHub Architecture

## Stage 1 Scope

Stage 1 creates the runnable foundation:

- Django backend with split settings, DRF, OpenAPI, Celery, and `/api/health/`.
- Vue 3 frontend with a portal shell and backend status check.
- PostgreSQL, Redis, Celery worker, Celery beat, Nginx, and Docker Compose.
- Persistent volumes for database, static files, public media, and protected media.

## Planned App Boundaries

- `accounts`: users, roles, approval, auth APIs.
- `portal`: public site settings, banners, research directions.
- `members`: team members and education/experience records.
- `news`: articles, tags, galleries, visibility.
- `publications`: papers, projects, patents, awards, standards, books.
- `documents`: protected document library, versions, permissions, download logs.
- `instruments`: instrument list, booking, training, maintenance, fault reports.
- `students`: student profile, milestones, archive files, thesis and defense records.
- `audit`: login, download, and important operation logs.
- `system`: health, site dictionaries, global configuration.
