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

## [Unreleased] — 2026-07-19

## [0.1.0] — Initial Planning Release

- Established core principles (James Clear + David R. Hawkins)
- Defined gap-filling mechanics and multi-tenant isolation rules
- Created operational documentation for AI-maintained codebase