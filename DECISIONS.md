# Waste No Time — Architectural and Product Decisions Log

## Confirmed Architectural & Functional Decisions

### 1. Philosophy & Core Principles
- **James Clear Trajectory Principle**: Awareness of current trajectory is far more important than end goals. Trajectory is defined as recency-weighted daily pace projected forward to the end of goal/calendar periods.
- **David R. Hawkins Principle ("Waste No Time / Straight and Narrow")**: Unaccounted time is eliminated using auto-gap-filling retroactively between activities. Capture friction is kept minimal with Telegram keypads.

### 2. Infrastructure & Stack
- **Framework**: Python + SQLite (`keyval.db` / SQLite DBs) as the single source of truth.
- **ManicTime Deprecation**: ManicTime integration (`manictime.py`, `manictime_dash.py`, MT endpoints) is completely removed.
- **Container Architecture**: Docker Compose + Makefile (`make up`, `make down`, `make test`, `make logs`, `make build`, `make backup`).

### 3. Activity Capture Mechanics
- **Gap-Filling Retroactive Logging**:
  When `/now <tag>, [notes]` is executed:
  1. The new activity's `start_time` is set to the `end_time` of the user's most recent activity (looking back up to 760 minutes).
  2. The new activity's `end_time` is set to `now`.
  3. The activity is persisted to SQLite.

### 4. Clean Feature Scope
- **Removed / Excluded**: Map of Consciousness (MOC) tags, `/basics` checklist, `/math` command, `/schedule` event planner.
- **Retained & Refined**: Core time tracking (`/now`, `/stop`, `/status`, `/last`, `/top`, `/budget`, `/key`, `/undo`), rich Telegram reply/inline markups, and SQLite persistence.

### 5. Testing & Operations
- **Testing**: pytest test suite (`test_tgb.py`, `test_db_server.py`, `test_sandbox.py`) running against isolated test environments.
- **Operations**: Makefile targets for Docker Compose (`make up`, `make down`, `make test`, `make logs`, `make build`, `make backup`).
