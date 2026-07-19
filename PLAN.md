# Waste No Time — Product and Technical Plan

## 1. Product thesis

**Waste No Time** is a personal trajectory system. It answers three questions:

1. **Where did my time actually go?**
2. **If I continue like this, where will my time go?**
3. **Is that predicted allocation aligned with the time budgets I chose for my goals?**

The product follows two principles:

- **Trajectory over distant outcomes:** recent repeated behaviour is more useful than an aspirational end state.
- **Straight and narrow:** reduce drift, distraction, and unnecessary complexity; make the next aligned action obvious.

This is not initially a general task manager, calendar, social network, or motivational content app. It is a private feedback loop:

> Define desired time allocation → capture actual activity → forecast trajectory → compare → correct the next action.

## 2. Decisions confirmed

- **Audience:** personal, single-user first.
- **Surfaces:** Telegram for low-friction capture and prompts; web dashboard for goals, analysis, and forecasts.
- **Capture model:** retain the reference bot's `/now <activity>, <notes>` workflow, recent-activity keyboard, interval prompts, reports, and time budgets.
- **Goal model:** goals are desired time spent on activity categories per day, week, or month.
- **Trajectory model:** predict future time allocation from historical time spent and compare it with the chosen allocation.
- **Default timezone:** `Pacific/Auckland`, configurable in settings.

## 3. Lessons from `telegrambot-learning`

### What is worth preserving

- `/now <tag>, <notes>` is a fast capture mechanism.
- Frequently/recently used tags on the Telegram keyboard reduce friction.
- Periodic checks ask what the user is doing when no activity is recorded.
- Daily, 7-day, monthly, top-activity, budget, CSV, and timesheet views contain the raw ingredients of trajectory awareness.
- Notes can be required for selected activities.
- ManicTime is a useful optional data source and can complement manual capture.
- Immediate feedback after logging—time spent on that activity today—is effective.

### What should not be carried forward

- The old bot is a large, tightly coupled module with command handlers, persistence, analytics, scheduling, and HTTP calls mixed together.
- It is hard-coded to one chat ID, server URL, activity list, budgets, and prompt wording.
- Goals are mostly placeholders or hard-coded strings rather than durable domain objects.
- A generic key-value table is used for structured concepts such as preferences and events.
- Activity retrieval in the current `main` branch is stubbed to an empty list, so ManicTime cannot be treated as the only source of truth.
- Some commands use unsafe `eval`, broad exception handling, global mutable state, and ambiguous units.
- Bot replies are often sent to the owner's chat instead of the initiating chat.
- Flask routes and data models are incomplete, tests cover only part of the system, and the latest GitLab pipeline is failing.

### Reuse strategy

Reuse the **interaction ideas and reporting concepts**, not the old implementation. Build a clean domain model and API, then make Telegram and the web app clients of the same application service.

## 4. Core concepts

### 4.1 Activity category

A stable category to which time is assigned, for example:

- Programming
- Writing
- Exercise
- Sleep
- Family
- Food
- Driving
- YouTube

Each category has:

- name and optional emoji/colour
- status: active or archived
- direction: `increase`, `maintain`, or `limit`
- optional parent category
- whether notes are required
- aliases for Telegram parsing/import matching

### 4.2 Time entry

A factual interval of time:

- category
- start and end timestamp
- duration (derived, never independently authoritative)
- optional note
- source: Telegram, web timer, web manual entry, or ManicTime
- external ID for import deduplication
- confidence/status: confirmed or inferred

Intervals must not overlap unless explicitly resolved. The system stores timestamps in UTC and displays them in the configured timezone.

### 4.3 Allocation goal

A desired amount of time for a category over a recurring period:

- category
- period: day, week, or month
- target duration
- goal type:
  - **at least** — e.g. programming ≥ 4 h/day
  - **at most** — e.g. YouTube ≤ 30 min/day
  - **range** — e.g. sleep 7–8 h/day
- effective start/end dates
- priority/weight

Goals are time budgets, not one-off deadlines. Equivalent daily rates are calculated for comparison, but the original period and value remain visible.

### 4.4 Check-in

A lightweight reflection linked to a moment or day:

- current activity (optional if already tracked)
- optional note
- optional consciousness/mood label retained from the old bot
- alignment response: on path / drifting / unsure

Consciousness labels are context, not an input that secretly changes the numerical trajectory score in MVP.

## 5. The trajectory model

### 5.1 Principle

The forecast must be understandable. The app should say, for example:

> At your recent pace, Programming is forecast at **82 h this month**, against a goal of **100 h**. You are **18 h behind trajectory**. A pace of **4 h 12 min/day** for the remaining 12 days would close the gap.

Avoid an opaque AI-generated score in the MVP.

### 5.2 Inputs

For each category:

- completed time in the current goal period
- recent daily time totals
- day-of-week pattern
- remaining time in the current period
- goal threshold/range
- data coverage (how much of each day was tracked)

### 5.3 MVP forecast

Use an explainable recency-weighted daily average:

1. Aggregate confirmed entries into local calendar-day totals per category.
2. Use the most recent 28 complete days when available.
3. Apply exponential recency weighting (default half-life: 7 days).
4. When at least four weeks exist, calculate separate weekday baselines to account for weekday/weekend behaviour.
5. Forecast remaining days in the current period using the matching daily/weekday baseline.
6. Add actual time already completed to forecast time remaining.
7. Show low confidence when fewer than 7 tracked days exist or tracking coverage is poor.

Core outputs:

- `actual_so_far`
- `forecast_period_total`
- `goal_target_or_range`
- `forecast_gap`
- `required_remaining_daily_pace`
- `recent_trend`: rising, steady, or falling
- `confidence`: low, medium, or high, with a reason

### 5.4 Alignment calculation

Calculate alignment per goal, not only one universal score:

- **At least goal:** progress toward target, capped for display at 100% aligned.
- **At most goal:** aligned while forecast is below the cap; show forecast overage otherwise.
- **Range goal:** aligned inside range; distance to nearest boundary outside it.

A dashboard-level **Trajectory Alignment** percentage may be a weighted aggregation of goal-level alignment, but every contribution must be inspectable. It must never hide the underlying hours.

### 5.5 “Straight and narrow” indicator

Represent focus without moral judgement:

- **On path:** forecast is inside the target/range.
- **Correction needed:** forecast misses target, but remaining required pace is feasible.
- **Off path:** forecast substantially misses target or required pace exceeds available time.
- **Insufficient evidence:** there is not enough tracked data.

The dashboard recommends at most one primary correction at a time: the highest-priority, largest actionable forecast gap.

### 5.6 Later forecasting upgrades

Only after sufficient real data and backtesting:

- compare EWMA against rolling mean and weekday-seasonal models
- prediction intervals
- automatic anomaly detection
- “what-if” allocation simulator
- model selection by walk-forward forecast error

No LLM is required for numerical forecasting. An LLM may later summarize already-computed facts, but it must not invent time or goals.

## 6. Primary user flows

### 6.1 First-run setup (web)

1. Connect a Telegram chat using a short-lived pairing code.
2. Confirm timezone and day boundary.
3. Create or select activity categories.
4. Set 3–7 allocation goals.
5. Choose check-in interval and quiet hours.
6. Optionally configure ManicTime later.

### 6.2 Capture in Telegram

- Tap `/now Programming` or type `/now Programming, API work`.
- The prior open activity ends at the new activity's start.
- A new activity starts immediately.
- Bot responds with:
  - activity started
  - time spent today and this week
  - goal pace status
  - recent-activity keyboard
- `/stop` closes the active interval.
- `/undo` reverses the latest capture safely.
- If a note is required and absent, the bot asks for it before confirming.

This preserves the old bot's capture style while making intervals explicit. The old four-second marker activity is not sufficient for forecasting actual duration.

### 6.3 Missed-time prompt

During configured waking/check-in hours, if no activity is open or recent coverage is missing:

- ask “What are you doing now?”
- show recent categories
- allow `Snooze`, `Untracked`, and `Quiet mode`
- rate-limit prompts and never send during quiet hours

### 6.4 Daily review

Telegram sends one compact review at the chosen time:

- tracked vs untracked time
- top categories
- goal pace: on path / correction needed
- one suggested correction for tomorrow
- link to dashboard

### 6.5 Dashboard review

The home dashboard shows:

1. **Current activity** and elapsed duration
2. **This period's allocation** as actual hours
3. **Forecast vs goal** for each category
4. **Trajectory trend** over 7/28 days
5. **One next correction**
6. **Coverage warning** when the evidence is incomplete

### 6.6 Correcting data

Web timeline supports:

- add a missed interval
- edit category, start/end, or note
- split and merge intervals
- resolve overlaps
- mark time untracked
- undo recent changes

## 7. Telegram command plan

### MVP commands

- `/start` — introduction or account pairing
- `/now <activity>, <optional note>` — stop current and start new activity
- `/stop` — stop current activity
- `/status` — current activity, today totals, and nearest trajectory correction
- `/today` — today's allocation and goal pacing
- `/week` — rolling/current week forecast and comparison
- `/month` — current month forecast and comparison
- `/goals` — concise list with a web link to edit
- `/undo` — undo latest activity transition
- `/settings` — web settings link
- `/help` — examples and commands

### Post-MVP commands

- `/top <period>`
- `/budget <activity>` as an alias/report
- `/note <text>`
- `/checkin`
- `/export`

Do not reproduce generic `/key`, `/math`, or owner-specific commands. Configuration belongs in typed settings and safe commands.

## 8. Web application information architecture

### Dashboard

- current activity/timer
- trajectory summary
- category forecast cards
- actual-vs-goal allocation chart
- next correction
- data coverage

### Timeline

- day/week timeline
- entry editor
- gap/overlap resolution
- source labels

### Goals

- create/edit/archive allocation goals
- daily/weekly/monthly units
- at least/at most/range controls
- effective dates and priority
- allocation feasibility warning (e.g. goals total more than available hours)

### Insights

- category trends
- forecast history vs actual outcome
- daily/weekly/monthly reports
- notes search

### Settings

- timezone/day boundary
- Telegram pairing
- prompts and quiet hours
- categories and aliases
- optional ManicTime connection
- export/delete data

## 9. Proposed technical architecture

Because this repository is currently effectively empty, start with a cohesive TypeScript monorepo rather than porting the Python script.

### Stack

- **Web/API:** Next.js with TypeScript
- **UI:** React, Tailwind CSS, accessible component primitives
- **Database:** PostgreSQL in deployed environments; local PostgreSQL via Docker
- **ORM/migrations:** Drizzle ORM
- **Validation:** Zod at all API boundaries
- **Bot:** grammY using Telegram webhooks in production
- **Jobs:** database-backed scheduled jobs/cron endpoint initially; a dedicated queue only when needed
- **Charts:** a small React charting library with accessible text/table equivalents
- **Tests:** Vitest for domain/unit tests, Playwright for critical web flows, API integration tests against an isolated database
- **Deployment:** containerized app plus managed PostgreSQL; exact host can be chosen at implementation time

### Modules

- `domain/activities` — interval rules and commands
- `domain/goals` — allocation goals and period normalization
- `domain/trajectory` — aggregation, forecasting, alignment, explanations
- `integrations/telegram` — updates, keyboards, pairing, replies
- `integrations/manictime` — optional adapter/importer
- `jobs` — prompts, reviews, imports, forecast snapshots
- `app` — web pages and route handlers

Telegram handlers and pages call application services; neither contains forecast logic.

### API shape

Representative endpoints:

- `POST /api/activities/start`
- `POST /api/activities/stop`
- `POST /api/activities/manual`
- `PATCH /api/activities/:id`
- `DELETE /api/activities/:id`
- `GET /api/activities?from=&to=`
- `GET/POST /api/categories`
- `GET/POST /api/goals`
- `PATCH/DELETE /api/goals/:id`
- `GET /api/trajectory?period=month`
- `GET /api/reports/daily`
- `POST /api/telegram/webhook`
- `POST /api/telegram/pair`
- `POST /api/imports/manictime/sync`

For the personal MVP, authentication can be a single owner account with secure session login. The schema should still include an owner/user ID so a later private beta does not require a data rewrite.

## 10. Data model

### Main tables

- `users`
  - `id`, `email`, `timezone`, `day_boundary`, timestamps
- `telegram_connections`
  - `user_id`, encrypted bot/chat identifiers as appropriate, pairing state, timestamps
- `categories`
  - `id`, `user_id`, `name`, `slug`, `color`, `direction`, `notes_required`, `archived_at`
- `category_aliases`
  - `category_id`, `alias`
- `activity_entries`
  - `id`, `user_id`, `category_id`, `started_at`, `ended_at`, `note`, `source`, `external_id`, `status`, timestamps
- `allocation_goals`
  - `id`, `user_id`, `category_id`, `period`, `goal_type`, `target_min_seconds`, `target_max_seconds`, `priority`, `effective_from`, `effective_to`
- `check_ins`
  - `id`, `user_id`, `occurred_at`, `alignment`, `consciousness_label`, `note`
- `user_settings`
  - typed prompt interval, quiet hours, review time, tracking preferences
- `forecast_snapshots`
  - period/category forecast values, confidence, model version, generated time
- `audit_events`
  - reversible activity edits and important settings changes
- `import_connections` / `import_runs`
  - source settings and sync state without logging secrets

### Important constraints

- category names unique per active user, case-insensitively
- end must be later than start
- only one open activity per user
- imported external IDs unique per source/user
- targets use integer seconds
- prevent or explicitly flag overlapping confirmed intervals
- all mutations are scoped to the owner

## 11. ManicTime plan

ManicTime is **optional**, not an MVP blocker, because the studied branch currently stubs activity retrieval.

Integration sequence:

1. Define a provider-neutral import interface.
2. Store server URL and token securely in environment/secret storage, never in logs.
3. Pull activities incrementally with a cursor/watermark.
4. Map ManicTime display names through category aliases.
5. Deduplicate by stable external IDs or deterministic source/time keys.
6. Put unmapped/overlapping imports in a reconciliation inbox.
7. Keep source provenance so imported entries can be re-synced safely.

Manual Telegram tracking remains fully functional without ManicTime.

## 12. Privacy and safety

- Single-user authorization on every endpoint, even before multi-user launch.
- Verify Telegram's webhook secret token.
- Pair a chat using a short-lived, one-time code; never hard-code chat IDs.
- Do not expose the Telegram bot token or ManicTime token to the browser.
- Encrypt integration credentials at rest when stored in the database.
- Avoid logging notes, tokens, or full Telegram payloads.
- Provide JSON/CSV export and complete deletion.
- Replace unsafe expression evaluation with explicit duration parsing.
- Use idempotency for webhook updates and imports.
- Back up the database and test restore procedures before relying on the app daily.

## 13. UX principles

- **Hours before scores:** always show the underlying actual, forecast, and target times.
- **One correction, not ten warnings:** prioritize the most useful next adjustment.
- **Neutral language:** “forecast gap” and “drift,” not guilt or failure.
- **Low capture friction:** a frequent activity should be loggable in one tap.
- **Calm by default:** no streak anxiety, public comparison, points, or noisy notifications.
- **Evidence honesty:** incomplete tracking produces lower confidence, not false precision.
- **Accessible:** keyboard navigation, readable contrast, semantic charts with table equivalents.

## 14. Delivery phases

### Phase 0 — Foundation and specification

- establish monorepo, linting, formatting, tests, CI, environment validation
- write architecture decision records
- implement database schema/migrations and seeded demo categories
- lock exact forecast formulas and period semantics in tests

**Exit:** clean build/test pipeline and executable domain tests for time periods and forecasts.

### Phase 1 — Activity capture core

- owner authentication
- categories
- start/stop/manual activity application services
- overlap/open-entry rules
- basic timeline and editor
- Telegram pairing, `/now`, `/stop`, `/status`, `/undo`
- recent-category keyboard

**Exit:** a full day can be reliably captured and corrected from Telegram/web.

### Phase 2 — Goals and trajectory MVP

- allocation-goal CRUD
- daily/weekly/monthly period calculations
- recency-weighted forecast
- confidence and coverage logic
- dashboard with actual/forecast/target and one correction
- `/today`, `/week`, `/month`, `/goals`

**Exit:** for every active goal, the user can understand current pace, predicted period total, gap, and required pace.

### Phase 3 — Feedback loop

- configurable prompt interval and quiet hours
- missed-time checks
- daily review
- check-ins/consciousness context
- scheduled forecast snapshots
- forecast-vs-outcome evaluation

**Exit:** capture → forecast → correction operates daily without manual dashboard checking.

### Phase 4 — Reports and portability

- insights/trend views
- CSV/JSON export
- timesheets and notes search
- backup/restore documentation

### Phase 5 — ManicTime integration

- secure connection
- incremental importer
- aliases/mapping and reconciliation
- deduplication and sync tests

### Explicitly deferred

- public signup and billing
- native mobile apps
- social/community features
- generalized tasks/projects/calendar
- LLM coaching
- complex machine-learning forecasts
- PDF/HTML report generation unless a concrete use case remains after CSV/dashboard delivery

## 15. Testing strategy

### Domain tests

- timezone and daylight-saving boundaries (especially Auckland transitions)
- daily/weekly/monthly period boundaries
- open activity transition and undo
- overlap prevention/splitting
- at least/at most/range alignment
- recency weighting and weekday seasonality
- low-data confidence
- required remaining pace
- goal effective-date changes

### Integration tests

- Telegram update idempotency and command parsing
- pairing and unauthorized chat rejection
- activity and goal API authorization/validation
- scheduled prompt quiet hours
- importer deduplication and mapping

### End-to-end tests

- setup → create goals → pair Telegram
- `/now` transition → dashboard reflects interval
- edit timeline → forecast recalculates
- daily review is generated from known fixture data

### Forecast quality tests

Keep historical fixtures and use walk-forward validation:

- forecast each past week/month using only data available at that point
- compare predicted and actual category hours
- record MAE/error by category and model version
- do not promote a more complex model unless it materially improves error and remains explainable

## 16. MVP acceptance criteria

The MVP is complete when:

1. The owner can pair Telegram securely.
2. `/now Category, note` ends the previous interval and starts the chosen one.
3. The owner can stop, undo, add, and correct activity entries.
4. The web app shows today's timeline and tracked/untracked coverage.
5. The owner can create at-least, at-most, and range time goals for day/week/month.
6. Each goal displays actual time, forecast total, target, forecast gap, trend, confidence, and required remaining pace.
7. Daily and monthly calculations respect `Pacific/Auckland`, including DST.
8. The bot can return concise today/week/month trajectory reports.
9. Prompts respect configurable intervals and quiet hours.
10. Data can be exported, and secrets/owner data are not exposed in logs or client code.
11. Core domain, API, and critical browser flows run in CI.

## 17. Initial success measures

For the first 30 days, measure product usefulness rather than growth:

- **capture coverage:** percentage of configured waking time assigned or explicitly untracked
- **capture friction:** median taps/messages to begin a frequent activity
- **review consistency:** days on which the daily trajectory was viewed
- **forecast calibration:** forecast error at week/month end
- **correction usefulness:** whether the primary gap improves after a recommended correction
- **goal clarity:** percentage of goals with unambiguous category, period, and threshold

Suggested personal targets:

- ≥ 80% tracking coverage during configured hours
- common activity capture in one tap
- daily review under 60 seconds
- forecast gap understandable without documentation

## 18. Recommended first implementation slice

Build one narrow vertical slice before the full dashboard:

1. owner login and timezone
2. two seeded categories
3. one monthly `at least` allocation goal
4. Telegram pairing
5. `/now` and `/stop`
6. persisted intervals
7. a single dashboard card showing actual, 28-day weighted forecast, target, and required remaining pace
8. deterministic tests around all calculations

This proves the product's central promise with the least code. Everything else should expand from this slice.

## 19. Open decisions before implementation

These can use sensible defaults but should be confirmed early:

1. **Day boundary:** midnight or a custom boundary such as 4:00 a.m. for late-night activity.
2. **Goal period meaning:** calendar week/month versus rolling 7/30 days. Recommended: calendar period for goals, rolling windows for trend context.
3. **Sleep tracking:** include the entire 24-hour day or focus prompts/coverage on configured waking hours.
4. **Active interval semantics:** `/now` starts a real open interval; confirm this replaces the old bot's short marker plus ManicTime repair behaviour.
5. **Authentication/deployment:** preferred owner login method and hosting provider.
6. **Bot ownership:** use a new Telegram bot token or the existing bot after feature parity.
7. **Visual direction:** calm/minimal, data-dense, or another preferred style.
