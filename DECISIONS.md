# Waste No Time — Architectural and Product Decisions Log

## Confirmed Architectural & Functional Decisions

### 1. Philosophy & Core Principles
- **James Clear Trajectory Principle**: Awareness of current trajectory is far more important than end goals. Trajectory is defined as recency-weighted daily pace projected forward to the end of goal/calendar periods.
- **David R. Hawkins Principle ("Waste No Time / Straight and Narrow")**: Unaccounted time is eliminated using auto-gap-filling retroactively between activities. Capture friction is kept minimal with Telegram keypads.

### 2. Infrastructure & Stack
- **Framework**: Django + SQLite (`db.sqlite3`) as the single source of truth.
- **API Approach**: Plain Django `JsonResponse` views without heavy frameworks like DRF or Ninja for web endpoints.
- **ManicTime Deprecation**: ManicTime integration (`manictime.py`, `manictime_dash.py`, MT endpoints) is completely removed.
- **Container Architecture**: Single container configuration (GitLab CE style) running both Django web server and Telegram bot daemon using `start.sh` managed via `docker-compose.yml`.
- **Operations**: Managed via Makefile (`make up`, `make down`, `make test`, `make logs`, `make build`).

### 3. Activity Capture Mechanics
- **Gap-Filling Retroactive Logging**:
  When `/now <tag>, [notes]` is executed:
  1. The new activity's `start_time` is set to the `end_time` of the user's most recent activity.
  2. The new activity's `end_time` is set to `now`.
  3. The activity is persisted to SQLite via Django ORM.
  4. The bot returns the time spent on that tag today along with the dynamic keypad.

### 4. Configuration, Reports & Timezones
- **Environment Variables**: Load `TELEGRAM_CHAT_ID` from environment (e.g. `.env.local`), falling back to `1040271347`.
- **Database Migrations**: `start.sh` executes `python manage.py migrate` automatically on container startup.
- **Timezone Standard**: Standardize database storage, timestamps, and reporting day boundaries on **UTC**.
- **Dual Reporting Formats**: Serve both plain HTML visual report documents (`/top`, `/summary`, `/timesheet`, `/calendar`) and structured JSON API endpoints.

### 5. Single Container Supervisor Pattern (GitLab CE Style)
- **start.sh Entrypoint**: Runs `python manage.py migrate`, launches Django HTTP web server in background, and executes `python manage.py run_bot` in the foreground.
- **Consolidated Persistence**: All models (`Activity`, `Goal`, `KeyValuePair`) stored in a single unified `db.sqlite3` file.

### 6. Document Exports & Testing
- **PDF Reports**: Maintain PDF attachments (`top.pdf`, `summary.pdf`) generated via FPDF.
- **Isolated Test Database**: All automated tests run against an isolated test database.
- **Dual Testing Strategy**:
  1. **Offline Unit & Integration Tests** (`make test`): Uses mocked Telegram API calls.
  2. **Live End-to-End Tests** (`make test-live`): Runs against the live Telegram API when `TELEGRAM_BOT_API_KEY` is provided.

### 7. Lookback & Gap-Filling Limits (Matching Legacy Code)
- **760 Minutes (12.67 Hours) Lookback**: Local gap-filling checks for the previous activity within the last 760 minutes.
- **Cold Start Bootstrap**: If no previous activity exists, the initial activity defaults to `now - 1 minute` → `now`.

### 8. Multi-Tenant User Isolation
- **Per-Chat Isolation**: Activities, goals, categories, key-value pairs, and check-in prompts are scoped per Telegram `chat_id`.

### 9. Waking-Hour Check-in Prompts
- **Periodic Check Prompts**: Background scheduler retains the `check()` periodic prompt behavior.

### 10. Django Project Structure
- **App Architecture**: Django project with core app `tracker` containing models for `Activity`, `Goal`, and `KeyValuePair`.

### 11. Ephemeral Document Generation (Zero Disk Accumulation)
- **On-the-Fly Generation**: Reports (PDF, HTML, CSV) are generated dynamically from the database and streamed directly.

### 12. Modern Bot Library & React Frontend Stack
- **Bot Library**: `python-telegram-bot` v21+ async polling daemon.
- **React Web Frontend**: Minimal Vite/React bundle served by Django at `/`.

### 13. Legacy Archiving & Helper Refactoring
- **legacy/ Directory Archival**: All obsolete files moved to `legacy/`.
- **Refactored Utility Modules**: Markup constants and helpers moved into `tracker/constants.py` and `tracker/helpers.py`.

### 14. Frontend Build, Keyboards, Data Seeding & Backups
- **Automated Docker React Compilation**: Dockerfile builds the React frontend.
- **Default Category Seeding**: Standard activity categories are seeded for new users.
- **Message-Attached Inline Keyboards**: Uses `InlineKeyboardMarkup`.
- **make backup Utility**: Added to Makefile.

### 15. Additional Decisions (2026-07-19)
- All planning documents (`DECISIONS.md`, `PLAN.md`, `TODO.md`, `CHANGELOG.md`, `AGENTS.md`) must be kept up to date.
- AI agents **must** run `npx repomix` before starting work.
- No code changes until explicit user approval to begin Phase 1.
- Single consolidated `db.sqlite3` only.

### 16. Dashboard Merge (2026-07-20)
- **Migrated from CRA to Vite**: The existing dash.lak.nz dashboard used Create React App; renamed all JSX-containing `.js` files to `.jsx` and configured Vite with `@vitejs/plugin-react`.
- **API consolidation**: Dashboard now fetches from Django's `/api/activities?chat_id=1040271347` instead of the separate actapi.lak.nz service.
- **Response adaptation**: A `transformData()` function in `App.jsx` maps Django's flat array (`name`, `start_time`, `end_time`) to the dashboard's expected shape (`displayName`, `startTime`, `endTime`), avoiding the need for a new Django endpoint or changes to the existing API.
- **Multi-stage Docker build**: Stage 1 (node:22-slim) builds the frontend; Stage 2 (python:3.11-slim) copies the built `dist/` and runs Django + bot.
- **Static file alignment**: Vite `base: '/static/'` with `assetsDir: ''` matches Django's `STATIC_URL = '/static/'` and `STATICFILES_DIRS = [frontend/dist]`, serving everything cleanly from one directory.
- The `docker-compose.yml` volume mount removed (`.:/app`) to prevent overriding the Dockerfile's built `dist/`; database persisted via `./db.sqlite3:/app/db.sqlite3`.

### 17. Dashboard Authentication (2026-07-21)
- The dashboard uses Telegram Login Widget only as an identity assertion. Django verifies the Telegram HMAC server-side using `TELEGRAM_BOT_API_KEY`, checks the assertion age, rotates the session ID, and stores the authenticated Telegram user ID in the session.
- Dashboard APIs derive tenant scope only from that session; they must never accept a user/chat identifier as an authorization input.
