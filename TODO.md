# Waste No Time — Implementation TODO List

## Phase 1: Codebase Cleanup & Infrastructure
- [ ] Move legacy files (`manictime.py`, `manictime_dash.py`, `db_server.py`, `keyvalue.py`, etc.) to `legacy/`
- [ ] Update `requirements.txt` with Django, `python-telegram-bot` v21+, `fpdf`, `pytz`, `gunicorn`
- [ ] Update `Dockerfile`, `docker-compose.yml`, and `start.sh` for single-container Django + bot setup
- [ ] Update `Makefile` with `up`, `down`, `test`, `test-live`, `logs`, `build`, `backup` targets
- [ ] Create `.env.sample` and `.env.local` (if needed)

## Phase 2: Django Core & Tracker Models
- [ ] Initialize Django project (`waste_no_time`) and `tracker` app
- [ ] Create `Activity`, `Goal`, and `KeyValuePair` models in `tracker/models.py`
- [ ] Create and run initial migrations
- [ ] Implement `gap_filler.py` with 760-minute lookback and cold-start logic

## Phase 3: Bot Command Migration (`python-telegram-bot` v21+)
- [ ] Create management command `tracker/management/commands/run_bot.py`
- [ ] Implement core handlers: `/now`, `/stop`, `/status`, `/last`, `/top`, `/budget`, `/key`, `/undo`
- [ ] Implement dynamic `InlineKeyboardMarkup` and gap-filling logic
- [ ] Implement background `check()` prompt loop

## Phase 4: Web Views & React Frontend
- [ ] Implement plain Django `JsonResponse` + HTML views in `tracker/views.py`
- [ ] Set up minimal Vite/React app in `frontend/` (served at `/`)
- [ ] Add basic dashboard showing recent activities and trajectory summary

## Phase 5: Testing & Verification
- [ ] Create `tracker/tests/` with Django `TestCase` suite
- [ ] Add tests for gap-filling, multi-user isolation, rate limits, strict notes
- [ ] Verify `make test` runs cleanly inside Docker
- [ ] Verify `make up` launches web server + bot successfully

## Documentation & Workflow
- [x] Create `AGENTS.md`, `DECISIONS.md`, `CHANGELOG.md`, `PLAN.md`, `TODO.md`
- [x] Run `npx repomix` and store output
- [ ] Keep all docs in sync on every change
- [ ] Archive legacy files instead of deleting them

**Current Status**: Still in planning phase. No code changes yet.