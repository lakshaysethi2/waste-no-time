# Waste No Time — Implementation TODO List

## Phase 1: Codebase Cleanup & Infrastructure
- [x] Move legacy files (`manictime.py`, `manictime_dash.py`, `db_server.py`, `keyvalue.py`, etc.) to `legacy/`
- [x] Update `requirements.txt` with Django, `python-telegram-bot` v21+, `fpdf`, `pytz`, `gunicorn`
- [x] Update `Dockerfile`, `docker-compose.yml`, and `start.sh` for single-container Django + bot setup
- [x] Update `Makefile` with `up`, `down`, `test`, `test-live`, `logs`, `build`, `backup` targets
- [x] Create `.env.sample` and `.env.local`

## Phase 2: Django Core & Tracker Models
- [x] Initialize Django project (`waste_no_time`) and `tracker` app
- [x] Create `Activity`, `Goal`, and `KeyValuePair` models in `tracker/models.py`
- [x] Create and run initial migrations
- [x] Implement `gap_filler.py` with 760-minute lookback and cold-start logic

## Phase 3: Bot Command Migration (`python-telegram-bot` v21+)
- [x] Create management command `tracker/management/commands/run_bot.py`
- [x] Implement core handlers: `/now`, `/stop`, `/status`, `/last`, `/top`, `/budget`, `/key`, `/undo`
- [x] Implement dynamic `InlineKeyboardMarkup` and gap-filling logic
- [x] Implement background `check()` prompt loop

## Phase 4: Web Views & React Frontend
- [x] Implement plain Django `JsonResponse` + HTML views in `tracker/views.py`
- [x] Set up minimal Vite/React app in `frontend/` (served at `/`)
- [x] Add basic dashboard showing recent activities and trajectory summary
- [x] Merge dash.lak.nz React dashboard into Django (Vite build, /api/activities, actapi decommissioned)

## Phase 5: Testing & Verification
- [x] Create `tracker/tests/` with Django `TestCase` suite
- [x] Add tests for gap-filling, multi-user isolation, rate limits, strict notes
- [x] Verify `make test` runs cleanly (offline part)
- [ ] Verify `make up` launches web server + bot successfully (requires valid bot token)

## Documentation & Workflow
- [x] Create `AGENTS.md`, `DECISIONS.md`, `CHANGELOG.md`, `PLAN.md`, `TODO.md`
- [x] Run `npx repomix` and store output
- [ ] Keep all docs in sync on every change
- [ ] Archive legacy files instead of deleting them

**Current Status**: Still in planning phase. No code changes yet.