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

## China Agricultural University Visual Identity

The local China Agricultural University Visual Identity System under `JPG/` is the design source of truth. Before changing the brand, navigation, homepage, major colors, typography, or decorative language, inspect the relevant manual pages rather than relying on memory or generic “university green” styling.

Key references:

- `JPG/A 基础部分/A1 基础设计要素/A1-1.01.jpg`: standard color mark.
- `JPG/A 基础部分/A1 基础设计要素/A1-1.22.jpg` through `A1-1.25.jpg`: Chinese and English type guidance.
- `JPG/A 基础部分/A1 基础设计要素/A1-1.26.jpg` and `A1-1.27.jpg`: “百年校门” and “韵动笔触” auxiliary graphics.
- `JPG/A 基础部分/A1 基础设计要素/A1-1.28.jpg` and `A1-1.29.jpg`: color strategy and exact auxiliary colors.
- `JPG/A 基础部分/A1 基础设计要素/A1-1.30.jpg` and `A1-1.31.jpg`: mark use on different backgrounds.

### Brand Hierarchy And Marks

- “中农雨磷” is the primary laboratory identity. “中国农业大学资源与环境学院” is the affiliation and should remain visually secondary.
- Do not make the portal look like an official university-wide website or imply that the laboratory logo is an official CAU mark.
- Never redraw, stretch, crop, rotate, recolor, outline, add effects to, or merge an official CAU mark with the laboratory logo. Use the supplied electronic asset and preserve its proportions and clear space.
- Choose the official standard, reversed, black, gold, or silver mark variant appropriate to the background. Do not place a low-contrast mark directly over a busy photograph.
- Keep the laboratory logo, CAU affiliation, page title, and navigation visually distinct. Do not repeat the same identity text in adjacent areas.

### Color System

The official primary color is CAU “生命绿”:

- 生命绿: `#00873C`

Official auxiliary colors from the local manual:

- 厚土金: RGB `162, 98, 42`, `#A2622A`
- 丰收金: RGB `151, 108, 8`, `#976C08`
- 喜悦金: RGB `248, 182, 45`, `#F8B62D`
- 典雅黄: RGB `219, 204, 174`, `#DBCCAE`
- 厚重绿: RGB `0, 61, 22`, `#003D16`
- 智慧蓝: RGB `0, 73, 94`, `#00495E`
- 理性蓝: RGB `0, 135, 169`, `#0087A9`
- 清新蓝: RGB `173, 200, 202`, `#ADC8CA`
- 淡雅绿: RGB `167, 211, 152`, `#A7D398`
- 雅致红: RGB `94, 0, 11`, `#5E000B`
- 知性红: RGB `199, 0, 63`, `#C7003F`
- 喜庆红: RGB `216, 33, 13`, `#D8210D`
- 睿智灰: RGB `159, 160, 160`, `#9FA0A0`
- 理性灰: RGB `201, 202, 202`, `#C9CACA`
- 起点灰: RGB `239, 239, 239`, `#EFEFEF`

Web application rules:

- Use white, warm white, and soft gray for most surfaces. Life green is an accent for primary actions, active navigation, links, short rules, icons, focus states, and important figures; do not flood entire pages with saturated green.
- Use 厚土金 sparingly as a warm agricultural accent and section differentiator. It must not compete with life green for primary actions.
- Use 厚重绿 for important headings or deep footer surfaces, and 理性蓝 for occasional informational states. Do not use every auxiliary color on one page.
- The manual’s suggested `70%` 厚土金, `5%` 理性蓝, `5%` 厚重绿, and `20%` other colors describes material-level color planning. It is not a literal CSS area quota for every screen.
- LabHub neutral tokens remain valid: warm background `#F8F7F2`, internal background `#F5F7F6`, body text `#2F3437`, muted text `#6B7280`, and border `#E5E7EB`.
- Keep shared colors and dimensions centralized in `frontend/src/styles/theme.css`. Do not scatter new brand hex values through components.

### Typography

- The manual specifies 汉仪大宋简、汉仪中宋简、汉仪书宋二简 for print Chinese, 汉仪大黑简、汉仪中黑简、汉仪中等线简 for office Chinese, Goudy Old Style for print English, and Myriad for office English.
- Treat those proprietary fonts as visual references only unless licensed webfont files are explicitly provided. Do not download, bundle, or substitute unlicensed font files.
- Browser font stack: `Noto Sans SC`, `Microsoft YaHei`, `PingFang SC`, `sans-serif`; English and numbers: `Inter`, `Arial`, `Helvetica`, `sans-serif`.
- Use restrained weights, normally `600` or `700` for headings and `400` or `500` for body and controls. Keep body line height near `1.7` and letter spacing at `0`.
- Use academic hierarchy rather than oversized marketing typography. Compact panels, cards, tables, and sidebars must use appropriately compact headings.

### Graphic Language

- The official auxiliary language is based on the “百年校门” main element and “韵动笔触” supporting element, generally following a flexible `1 + 2` composition principle.
- Use official auxiliary artwork only when the supplied asset is available. Do not manually trace or invent a near-copy of the gate, brush stroke, seal, or university mark.
- For the web UI, this language may be translated into restrained architectural linework, short green/gold rules, quiet borders, and generous spacing. Decoration must stay subordinate to content.
- Prefer authentic campus, team, fieldwork, composting, microbiology, and laboratory photography. Avoid generic stock scenes, neon science imagery, fake data dashboards, and decorative imagery that obscures people or research objects.

### Public Portal

- The public portal should feel academic, open, calm, and connected to agriculture, resources, environment, ecology, composting, and microbiology. It must not feel like a generic SaaS landing page.
- Use a clear content line shared by navigation, banner, and page sections. Allow breathing room but avoid large empty zones that make wide screens feel scattered.
- The home banner is a CMS-managed photo carousel. Keep its controls subtle, preserve useful focal points on desktop and mobile, and keep title/subtitle modest enough not to cover people.
- Keep section introductions concise. Never duplicate section names, summaries, research-direction copy, affiliation, contact information, or calls to action in adjacent blocks.
- Cards should be compact and purposeful, normally `4px` to `10px` radius with a thin border and minimal shadow. Do not turn every section into a floating card.
- Life green and 厚土金 may form a small dual-color rule or local accent, but not a heavy decorative frame around every section.

### Internal Platform

- Use the same identity with a quieter, work-focused layout: soft gray page background, white content surfaces, clear borders, compact controls, and predictable alignment.
- Keep primary action placement consistent across accounts, student archives, instruments, documents, and CMS pages.
- Avoid oversized page descriptions, isolated metric rows, excessive nested cards, and wide empty margins on large displays.
- Dense repeated data needs search, sorting where useful, pagination, compact rows, readable empty states, and actions that do not crowd the main content.
- On mobile, navigation and all CMS tabs must remain reachable. Tables and forms must reflow intentionally instead of being silently clipped.

### Accessibility And Quality Gate

- Maintain readable contrast for text, controls, and marks. Do not rely on color alone for status; pair it with text or an icon.
- Preserve visible keyboard focus, adequate touch targets, and reduced-motion-friendly behavior.
- Text, navigation, pagination, upload controls, and media must not overflow or become inaccessible at common desktop, 2K, tablet, and phone widths.
- After a visual change, inspect representative public and internal pages on desktop and mobile, then run the frontend build and relevant visual/end-to-end tests.
- If an official print rule conflicts with web accessibility or product usability, preserve the identity intent while prioritizing accessibility, and document the exception in the change.

### Prohibited Visual Patterns

- No flashy technology aesthetic, neon glow, complex gradients, glassmorphism, particle effects, decorative orbs, or “big-screen command center” dashboards.
- No excessive shadows, nested cards, pill-shaped navigation masks, oversized rounded containers, or strong hover motion.
- No one-note all-green page, and no arbitrary mixture of green, gold, red, and blue for decoration.
- No duplicate headings or explanatory text that merely repeats visible interface labels.
- No unofficial CAU-style seal, gate drawing, or homemade institutional mark.

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
