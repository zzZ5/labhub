# LabHub Agent Notes

This file is for future coding agents working on LabHub. It summarizes the project shape, local conventions, and the fragile points that should be respected during maintenance.

## Project Overview

LabHub is a laboratory public portal plus internal research management platform for “中农雨磷”, affiliated with 中国农业大学资源与环境学院.

Core stack:

- Backend: Django, Django REST Framework, PostgreSQL, Redis, Celery.
- Frontend: Vue 3, TypeScript, Vite, Pinia, Vue Router, Element Plus.
- Runtime: Docker Compose for both development and production.
- Public website: portal pages under `frontend/src/views/portal/`.
- Internal platform: dashboard/CMS/documents/instruments/students/members under `frontend/src/views/`.
- CMS API: Django viewsets under `backend/apps/system/cms_views.py`, routes under `backend/apps/system/cms_urls.py`.

## Important Directories

- `backend/apps/accounts/`: authentication, roles, permissions, member/user linkage.
- `backend/apps/portal/`: public site settings, research directions, home banners, contact info.
- `backend/apps/members/`: public/internal member data.
- `backend/apps/news/`: news categories, articles, Word-derived HTML, gallery images.
- `backend/apps/publications/`: papers, projects, patents, awards.
- `backend/apps/documents/`: internal documents and preview/download logic.
- `backend/apps/instruments/`: internal instrument platform. No reservation workflow is wanted.
- `backend/apps/students/`: student archive records and uploaded archive files.
- `backend/apps/system/`: CMS, upload helpers, image compression, health/CSRF endpoints.
- `frontend/src/api/`: API wrappers. Keep API paths centralized here.
- `frontend/src/layouts/PortalLayout.vue`: public site navigation/footer.
- `frontend/src/layouts/InternalLayout.vue`: internal platform shell.
- `frontend/src/views/cms/PortalCms.vue`: internal portal content editor. This page is important and often edited.
- `frontend/src/views/portal/PortalHome.vue`: public home page.
- `frontend/src/styles/theme.css`: global visual tokens.

## Run And Verify

Development:

```bash
docker compose up --build
```

Open:

- Frontend dev server: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Health: `http://localhost:8000/api/health/`

Common verification:

```bash
docker compose exec frontend npm run build
docker compose exec backend python manage.py test
git diff --check
```

If only frontend changed, at minimum run:

```bash
docker compose exec frontend npm run build
git diff --check -- frontend
```

Production deploy uses:

```bash
bash deploy/scripts/deploy.sh
bash deploy/scripts/restart.sh
```

Production Compose exposes Nginx on `NGINX_HTTP_PORT`, default `8088`. The user has used `/srv/labhub` on Ubuntu and cpolar with `labhub.cpolar.cn`.

## Environment And Secrets

- Never commit `.env`.
- Use `.env.example` and `.env.production.example` as templates.
- Production `.env` controls domains, CSRF/CORS, admin bootstrap values, ports, database password, etc.
- If login works by username but not email, check the custom authentication backend/serializer before resetting data.
- If redeploy loses newly created accounts, suspect database volume or wrong compose file/project rather than password first.

## Public Portal CMS Contract

Most public website content should be editable in internal “门户内容”.

Key mapping:

- “站点首页”
  - `site_name`: lab/site name.
  - `site_subtitle`: affiliation shown in navigation/footer, not forced into every hero text.
  - `keywords`: homepage hero subtitle fallback.
  - `description`: homepage “课题组简介”.
  - `hero_image`: default home banner image used only when no dedicated home banner exists.
  - `logo` and `favicon`: public brand images.
  - `external_links`: footer links.
- “首页横幅”
  - `title`: title shown on that banner.
  - `subtitle`: subtitle shown on that banner.
  - `image`: banner photo.
  - `sort_order`: ordering.
  - `is_active`: public display switch.

Important banner bug fixed: `HomeBanner.image` can be `null` if a banner was created without an image. Frontend display helpers must handle empty/null image values and show “未上传图片” instead of crashing the whole CMS list.

Do not use labels like “横幅显示标题” or “横幅兜底副标题”. The user prefers plain labels such as “标题” and “副标题”.

## Design Direction

Public portal style should be:

- Simple, academic, clean, CAU-style green.
- Agricultural ecology and resource/environment feel.
- Avoid flashy tech style, heavy gradients, glassmorphism, big data dashboard visuals, excessive cards, or strong shadows.
- Avoid duplicate section labels. Do not show “研究方向 / 研究方向” or “加入我们 / 联系我们” redundantly.
- Public home should not feel like a generic SaaS template.

Core colors:

- CAU life green: `#00873C`
- Deep green: `#1F3D2B`
- Rice background: `#F8F7F2`
- Soft gray: `#F5F7F6`
- Text: `#2F3437`
- Muted: `#6B7280`

Homepage notes:

- The home banner is a photo carousel managed by CMS.
- Banner width should align with the global content container and navigation content line.
- Keep a small gap between fixed navigation and banner.
- Banner text should be modest in size and show title/subtitle only.
- “课题组简介” should stay concise and should not repeat research directions. Research directions have their own section.

Internal platform style:

- Use the same brand but more management-oriented.
- Background `#F5F7F6`, white content surfaces, restrained borders.
- Mobile internal pages need special attention; tables/lists should not overflow horizontally.
- Dense repeated data should support search, pagination, compact rows, and clear actions.

## Data And Permission Conventions

User account identity and school/lab identity are separate:

- `UserProfile.school_identity`: supervisor, postdoc, PhD student, master student, undergraduate, or other.
- `UserProfile.membership_status`: active or former (graduated/left); this does not control login.
- System permissions in `UserRole`: admin, editor, document manager, and instrument manager only.
- A user may be both supervisor and admin.
- A supervisor is not automatically an administrator and does not automatically receive portal, document, instrument, or account-management permissions.
- Login should allow username or email.
- Graduation or departure preserves the account, student archive, and historical files. `User.is_active` separately controls whether login is allowed.
- Approved users without system permissions can browse internal content and maintain their own student archive, but cannot manage portal content, instruments, documents, or accounts.

Students:

- Advisors are allowed and students may have multiple advisors.
- Advisors do not need generated student archive records.
- One account should not have multiple student archives.
- Member management should support creating accounts and one-click archive generation where appropriate.
- Student lists should support many students, compact rows, search, filters, and pagination.

Documents/uploads:

- Internal documents and student archive files should support preview where possible, not just download.
- PDF can be embedded directly.
- Word/PPT preview is conversion-based where available; do not promise browser-native Word/PPT rendering.
- Large uploads should show progress. Current upload target has been tuned for large files up to about 200 MB and slow links.
- Student archive files should not show unnecessary version labels by default.
- Permissions: admins and file owners have stronger control; ordinary members should only operate their own uploaded internal files unless explicitly permitted.

Instruments:

- Instruments belong in the internal platform, not public website.
- No reservation workflow is wanted; offline usage is recorded separately.
- Instrument list should support search and many items.
- Instrument detail should show image, status, location/contact if available, and usage instructions.
- Avoid complex equipment-number/admin-heavy fields unless explicitly requested.

News:

- Public news categories should stay simple: 学术交流, 组内动态, 科研进展, 成果荣誉, 招生招聘, 项目相关.
- News detail pages should be clickable from lists/home.
- Word news uploads may generate HTML content; only show converted content after processing completes.
- Avoid duplicated images after Word conversion.

Publications/projects/patents/awards:

- Papers can be numerous; use pagination/search/detail pages.
- Projects, patents, and awards are separate categories.
- Project public display should be concise and not expose sensitive detail.
- Papers/patents/awards may have PDF/image attachments and should support view/download where applicable.
- Import templates live under `frontend/public/import-templates/`.

## API Patterns

Frontend API base is configured in `frontend/src/api/http.ts`:

- Dev/proxy default: `/api`
- Media URL normalizer rewrites backend-local media URLs to `/media/...`.
- Keep API wrappers in `frontend/src/api/` rather than hardcoding endpoints in Vue components.

Public routes:

- `/api/portal/`
- `/api/members/`
- `/api/news/`
- `/api/publications/`

CMS routes:

- `/api/cms/site-settings/`
- `/api/cms/contact-info/`
- `/api/cms/home-banners/`
- `/api/cms/research-directions/`
- `/api/cms/members/`
- `/api/cms/news-*`
- `/api/cms/publications/`
- `/api/cms/projects/`
- `/api/cms/patents/`
- `/api/cms/awards/`
- `/api/cms/instruments/`

When adding a CMS-managed public model, update all of:

- Django model/serializer/viewset/routes.
- Frontend public API type.
- Frontend CMS API methods.
- `PortalCms.vue` editor/list rows.
- Public page display.

## Deployment Notes

Production compose:

- `docker-compose.prod.yml`
- Backend: Gunicorn timeout is long for slow uploads/conversions.
- Nginx default ports: `8088` and `8443`.
- Volumes: `staticfiles`, `media`, `protected_media`, `frontend_dist`, `postgres_data`.

If port 80 is occupied by host Nginx/Apache, do not bind project Nginx to port 80. Use `NGINX_HTTP_PORT=8088` or another free port.

If cpolar forwards to local service:

- Forward HTTP to the Nginx exposed port, commonly `127.0.0.1:8088`.
- Configure allowed hosts/CSRF origins to include the cpolar domain.

If deployment returns 502:

- Check Nginx logs first.
- Check backend container state and logs.
- Make sure `deploy.sh` brought up backend and ran migrations.
- Check whether backend is still starting; do not assume it is an auth problem.

Useful production commands:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## Editing Guidelines

- Keep changes scoped. Do not refactor unrelated modules while fixing UI details.
- Preserve user data and database volumes.
- Do not delete existing media or protected media unless explicitly requested.
- Use existing Vue/Element Plus patterns; avoid adding a new UI framework.
- Use `apply_patch` for manual edits.
- Keep Chinese UI text concise and natural. Avoid engineering labels in user-facing UI.
- Prefer defensive frontend code for nullable API fields.
- Do not create public placeholders unless the user asks. Empty CMS content should show clean empty states.
- Avoid hidden duplicate content: if a module has its own section, do not repeat it in intro text.

## Current Verification Baseline

As of this note, frontend build has been run successfully in Docker with:

```bash
docker compose exec frontend npm run build
```

Rollup may warn about large chunks or comments in dependencies; those warnings are not currently blocking.
