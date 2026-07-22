# Legacy Archive — Do Not Import

This directory contains the pre-Django implementation of the Telegram bot and associated scripts.
It is kept **only for historical reference** and for AI agents to understand previous interaction patterns.

**Rules:**

- **Do not import from `legacy/` into the new Django app (`tracker/`, `waste_no_time/`).** The old code uses unsafe patterns (eval, global mutable state, hard-coded chat IDs) and does not respect multi-tenant isolation.
- **Do not add new tests that depend on `legacy/` code.** The only file that may be imported in tests is the isolated `merge_case_duplicates` helper if explicitly required — but prefer re-implementing logic in `tracker/`.
- **Do not deploy files from `legacy/`.** They are not included in the Docker image's Python path for production.
- If you need an idea from the old bot, read the file, extract the *interaction* concept, and re-implement cleanly in `tracker/management/commands/run_bot.py` with proper Django ORM scoping (`telegram_chat_id` filter).

If you are an AI agent and you find yourself reaching for `legacy/`, stop and check `PLAN.md` and `DECISIONS.md` for the canonical design first.
