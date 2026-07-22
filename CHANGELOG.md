# Changelog

All notable changes to the **Waste No Time** personal trajectory and activity tracking system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [Unreleased]

### Security
- Dashboard API endpoints now require a server-side session established by a verified Telegram Login Widget payload. Query-string `chat_id` values no longer select tenant data.
- Removed the hard-coded dashboard chat ID and browser-only username allow-list.
- Production settings now require `DJANGO_SECRET_KEY`, default `DJANGO_DEBUG` to `False`, and enable secure-cookie, HSTS, MIME-sniffing, and clickjacking protections.

### Changed
- Docker now builds the Vite dashboard in a multi-stage image build; `start.sh` collects static files and exits if either Gunicorn or the bot exits.
- Dashboard activity responses use the camel-case client contract (`displayName`, `startTime`, `endTime`) and are covered by API authentication/isolation tests.
- Added the required `VITE_TELEGRAM_BOT_USERNAME` deployment setting.

### Added
- Merged dash.lak.nz React dashboard into Django project: single-container serves both API and frontend.
- Multi-stage Dockerfile builds Vite/React frontend before Python stage; `docker compose up --build` provides end-to-end service.
- Dashboard fetches from `/api/activities?chat_id=1040271347` (Django ORM), replacing the legacy actapi.lak.nz backend.
- Response transformation maps Django flat array (`name`, `start_time`, `end_time`) to dashboard's expected shape (`displayName`, `startTime`, `endTime`).

## [Unreleased]

### Added (earlier)
- `/tz <zone>` command to set per-user timezone (stored in `KeyValuePair` with key `tz`, defaults to `UTC`).
- Timezone picker buttons in `/settings` inline keyboard (UTC, Pacific/Auckland, America/New_York, Europe/London, Asia/Tokyo, Australia/Sydney).
- `_format_time()` helper that converts UTC datetimes to the user's timezone and formats with the abbreviation (e.g. `14:30 NZST`).

### Changed
- `/now`, `/status`, and `/last` commands now display times in the user's configured timezone with abbreviation.
- `/top` chart label includes the user's timezone abbreviation (e.g. `last 24h (NZST)`).
- `/settings` now shows the current timezone in the summary.
- `/help` lists the new `/tz` command.

### Fixed
- Rate limit on `/now` now checks the last Activity's `start_time` in the database instead of the `last_called` KV (which the bot's own periodic check was also writing to, causing false rejections).
- Duration recalculation on activity merge: `save(update_fields=['end_time'])` skipped the model's custom `save()` so `duration` never updated; now uses full `save()`.

### Changed
- `/now` response cleaned up: no more activity keyboard after a successful log, keeping the original check prompt intact on button presses.
- Rate limit errors on inline button presses now show a temporary popup (`show_alert=True`) instead of a new chat message.
- `/top` argument now interpreted as hours instead of days (e.g. `/top 0.5` = last 30 min, `/top 2` = last 2h, default 1h). Accepts float values.
- `/top` now sends an inline doughnut chart (matplotlib) with the text summary. Accepts optional day count e.g. `/top 7`.
- Activity selection keyboard is now paginated: 6 per page with `<` / `>` navigation and page counter.
- `Activity.duration` is now a computed `@property` instead of a stored DB column — eliminates stale-data vectors (migration `0002_remove_activity_duration`).
- `/start` sends `ReplyKeyboardRemove` to clear any stale reply keyboard from the legacy bot.

## [0.1.0] — Initial Planning Release

- Established core principles (James Clear + David R. Hawkins)
- Defined gap-filling mechanics and multi-tenant isolation rules
- Created operational documentation for AI-maintained codebase