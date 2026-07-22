# Changelog

All notable changes to the **Waste No Time** personal trajectory and activity tracking system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- Dashboard API endpoints now require a server-side session established by a verified Telegram Login Widget payload. Query-string `chat_id` values no longer select tenant data.
- Removed the hard-coded dashboard chat ID (`1040271347`) and browser-only username allow-list (`lakshaynz`).
- Production settings now require `DJANGO_SECRET_KEY`, default `DJANGO_DEBUG` to `False`, and enable secure-cookie, HSTS, MIME-sniffing, and clickjacking protections.
- `DJANGO_ALLOWED_HOSTS` warns in production if not explicitly set (prevents silent Cloudflare tunnel 400s).
- Removed unused stub `Minnion.jsx` (dead code, never imported).

### Added
- Merged dash.lak.nz React dashboard into Django project: single-container serves both API and frontend.
- Multi-stage Dockerfile builds Vite/React frontend before Python stage; `docker compose up --build` provides end-to-end service.
- Dashboard activity responses use the camel-case client contract (`displayName`, `startTime`, `endTime`) and are covered by API authentication/isolation tests.
- Added the required `VITE_TELEGRAM_BOT_USERNAME` deployment setting.
- `/tz <zone>` command to set per-user timezone (stored in `KeyValuePair` with key `tz`, defaults to `UTC`).
- Timezone picker buttons in `/settings` inline keyboard (UTC, Pacific/Auckland, America/New_York, Europe/London, Asia/Tokyo, Australia/Sydney).
- `_format_time()` helper that converts UTC datetimes to the user's timezone and formats with the abbreviation (e.g. `14:30 NZST`).
- Trajectory now respects user's timezone: period boundaries (day/week/month) and 28-day EWMA buckets are computed in local calendar, then converted to UTC for DB queries.
- `legacy/README.md` warning not to import from legacy archive.
- New test `test_trajectory_respects_user_timezone` verifies timezone-aware bucketing.

### Changed
- Docker now builds the Vite dashboard in a multi-stage image build; `start.sh` collects static files and exits if either Gunicorn or the bot exits.
- `run_bot.py` now uses `Application.run_polling()` instead of manual `initialize/start/updater.start_polling` with custom SIGTERM handling — the library's documented pattern.
- Centralized magic numbers into named constants: `DEFAULT_CHECK_INTERVAL_SECONDS`, `MIN/MAX_CHECK_INTERVAL_SECONDS`, `CHECK_JOB_INTERVAL_SECONDS`, `ACTIVITY_KEYBOARD_PAGE_SIZE`, `RATE_LIMIT_SECONDS`.
- `/now`, `/status`, and `/last` commands now display times in the user's configured timezone with abbreviation.
- `/settings` now shows the current timezone in the summary and uses named interval constants.
- `/help` lists the new `/tz` command.
- `/now`, `/status`, `/last`, `get_today_total` all respect user's configured timezone for day boundaries.
- Donut chart legend moved to `center left` with `bbox_to_anchor=(1,0.5)` and `bbox_inches='tight'` to prevent clipping.
- `Number.jsx` magic index `which_to_show=3` replaced with `DEFAULT_PERIOD_INDEX` and `PERIOD_LABELS`.
- `App.jsx` uses `useCallback` for `getData` and declares proper `useEffect` deps; filters null entries from tag maps.
- `LastUpdated.jsx` simplified — removed theme toggle that mutated parent background.
- Trajectory test `test_trajectory_simple` now freezes time to 2026-07-15 mid-month via `unittest.mock.patch`, eliminating brittleness when run on 1st–7th of month.

### Fixed
- Rate limit on `/now` now checks the last Activity's `start_time` in the database instead of the `last_called` KV (which the bot's own periodic check was also writing to, causing false rejections).
- `get_today_total` previously used UTC midnight for "today" — now uses user's local midnight.
- Activity duration no longer goes stale on merge (uses full `save()` not `update_fields=['end_time']`).
- `Activity.duration` is now a computed `@property` instead of stored column (migration `0002_remove_activity_duration`).

### Removed
- `frontend/src/components/molecules/Minnion.jsx` — unused placeholder that rendered a 300px div with "Driving".

## [0.2.0] — 2026-07-19

### Added
- Initialized Django project `waste_no_time` and `tracker` app.
- Implemented core models: `Activity`, `Goal`, `KeyValuePair`.
- Implemented `gap_filler.py` for retroactive activity logging (760m lookback).
- Implemented `trajectory.py` for exponential recency-weighted pace forecasting.
- Refactored Telegram bot into Django management command `run_bot` using `python-telegram-bot` v22.
- Added dynamic inline keyboards for quick activity capture.
- Integrated Vite/React frontend, served directly by Django.
- Updated infrastructure: `Dockerfile`, `docker-compose.yml`, `Makefile`, `start.sh`.
- Added test suites for gap-filling and trajectory engines.

### Changed
- Moved legacy files to `legacy/` directory.
- Consolidated all persistence into unified `db.sqlite3`.
- Replaced ManicTime dependency with local retroactive capture logic.

## [0.1.0] — Initial Planning Release

- Established core principles (James Clear + David R. Hawkins)
- Defined gap-filling mechanics and multi-tenant isolation rules
- Created operational documentation for AI-maintained codebase
