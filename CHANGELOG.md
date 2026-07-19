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

### Fixed
- Rate limit on `/now` now checks the last Activity's `start_time` in the database instead of the `last_called` KV (which the bot's own periodic check was also writing to, causing false rejections).
- Duration recalculation on activity merge: `save(update_fields=['end_time'])` skipped the model's custom `save()` so `duration` never updated; now uses full `save()`.

### Changed
- `/now` response cleaned up: no more activity keyboard after a successful log, keeping the original check prompt intact on button presses.
- Rate limit errors on inline button presses now show a temporary popup (`show_alert=True`) instead of a new chat message.
- `/top` now sends an inline doughnut chart (matplotlib) with the text summary. Accepts optional day count e.g. `/top 7`.
- Activity selection keyboard is now paginated: 6 per page with `<` / `>` navigation and page counter.
- `Activity.duration` is now a computed `@property` instead of a stored DB column — eliminates stale-data vectors (migration `0002_remove_activity_duration`).
- `/start` sends `ReplyKeyboardRemove` to clear any stale reply keyboard from the legacy bot.

## [0.1.0] — Initial Planning Release

- Established core principles (James Clear + David R. Hawkins)
- Defined gap-filling mechanics and multi-tenant isolation rules
- Created operational documentation for AI-maintained codebase