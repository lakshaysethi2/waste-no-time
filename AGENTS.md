# Instructions & Technical Guidelines for AI Coding Agents

Welcome to **Waste No Time**! This repository is designed to be maintained primarily by AI coding agents.

> ⚠️ **MANDATORY DIRECTIVE FOR AI AGENTS**:
> Every time you start a new task or onboard to this repository, you **MUST** run:
> ```bash
> npx repomix
> ```
> (or `repomix`) to pack the entire codebase into a single context file before reading any code.

## Quick Orientation

### File & Directory Map
```
.
├── AGENTS.md            # ← You are here
├── DECISIONS.md         # All architectural decisions
├── CHANGELOG.md
├── PLAN.md              # Full system specification
├── TODO.md              # Execution checklist
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── start.sh
├── requirements.txt
├── waste_no_time/       # Django project (to be created)
├── tracker/             # Core Django app (to be created)
├── frontend/            # Vite/React (to be created)
└── legacy/              # Archived old code
```

## Core Rules for AI Agents

1. **Single Source of Truth** — Only `db.sqlite3` via Django ORM. Never create `keyval.db` or `my_database2.db`.
2. **Multi-Tenant Isolation** — Every query must filter by `user_id` (Telegram `chat_id`).
3. **Gap-Filling Logic** — 760-minute lookback, cold-start = 1-minute interval.
4. **Ephemeral Reports** — Generate PDFs/HTML/CSV in memory only.
5. **Single Container** — Django web + bot run together via `start.sh`.
6. **Documentation First** — Update `CHANGELOG.md`, `DECISIONS.md`, `TODO.md` on every change.

## Development Workflow

1. Run `npx repomix`
2. Read `PLAN.md`, `DECISIONS.md`, `TODO.md`
3. Make changes
4. Run tests (`make test`)
5. Update documentation
6. Commit with clear message

## Command Reference
```bash
npx repomix
make up
make down
make test
make logs
python manage.py runserver
python manage.py run_bot
```

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
