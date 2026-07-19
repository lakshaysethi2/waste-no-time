# Changelog

All notable changes to the **Waste No Time** personal trajectory and activity tracking system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — 2026-07-19

### Added
- Comprehensive planning artifacts: `AGENTS.md`, `DECISIONS.md`, `CHANGELOG.md`, `PLAN.md`, `TODO.md`
- `repomix-output.xml` (full repository context for AI agents)
- Mandatory Repomix directive for all future AI agents
- Detailed architectural decisions and polar-question alignment process
- Single-container Docker + Makefile operational model (GitLab CE style)
- Django + SQLite + python-telegram-bot v21+ architecture blueprint
- Gap-filling logic specification (760-minute lookback, cold-start, strict notes)

### Changed
- Project direction shifted from ManicTime-dependent Flask/Peewee stack to clean Django-based system
- All future work must follow documented decisions and use Repomix for context

### Deprecated / Removed (planned for Phase 1)
- ManicTime integration (`manictime.py`, `manictime_dash.py`)
- Fragmented storage (`keyval.db`, `my_database2.db`)
- Unsafe commands (`/math` with `eval()`)
- Legacy Flask server and old test files

## [0.1.0] — Initial Planning Release

- Established core principles (James Clear + David R. Hawkins)
- Defined gap-filling mechanics and multi-tenant isolation rules
- Created operational documentation for AI-maintained codebase