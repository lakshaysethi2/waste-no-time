# Telegram Bot - Learning Project

A Telegram bot for time tracking, goal setting, and personal productivity. Integrates with ManicTime for activity tracking and provides rich reporting via Telegram messages.

## Features

- **Time Tracking**: Log activities with `/now <tag>` command
- **Activity Reports**: `/top`, `/summary`, `/evening` for time analysis
- **Goal Management**: Set and track personal goals
- **Key-Value Store**: Persistent key-value database (`/key`, `/append`, `/del`)
- **Scheduling**: Schedule events and get reminders
- **Inline Reply Markup**: Smart keyboard with recently used tags
- **CSV/HTML/PDF Exports**: Export timesheets and summaries
- **Budget Tracking**: Monitor daily/weekly time budgets per activity
- **ManicTime Integration**: Full integration with ManicTime Server API

## Quick Start with Docker

### Prerequisites

- Docker
- A Telegram Bot API key (from [@BotFather](https://t.me/BotFather))

### Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd telegrambot-learning
   ```

2. Copy the environment sample and configure:
   ```bash
   cp .env.sample .env.local
   ```

3. Edit `.env.local` with your Telegram Bot API key:
   ```
   TELEGRAM_BOT_API_KEY=your_bot_api_key_here
   PRODUCTION=0
   DEBUG=0
   ```

4. Run with Docker Compose:
   ```bash
   docker compose up -d
   ```

### Manual Docker Build

```bash
docker build -t tgb .
docker run --rm -v $(pwd)/.env.local:/app/.env.local tgb
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_API_KEY` | Telegram Bot API token | Yes |
| `PRODUCTION` | Set to `1` for production mode | No |
| `DEBUG` | Enable debug logging | No |
| `MANICTIME_AUTH_TOKEN` | ManicTime auth token | For ManicTime features |

## Project Structure

```
telegrambot-learning/
├── main.py                # Bot entry point and command handlers
├── db_server.py           # Flask REST API for activities/users
├── manictime.py           # ManicTime integration module
├── keyvalue.py            # Persistent key-value store (Peewee/SQLite)
├── variables.py           # Shared markup and configuration
├── goals.py               # Goal management functions
├── assistant.py           # Assistant functionality
├── calendarfile.py        # Calendar HTML generation
├── conversationBot.py     # Conversation handler
├── dynalist.py            # Dynalist integration
├── manictime_dash.py      # ManicTime dashboard
├── scheduleTagCheck.py    # Scheduled tag checking
├── readdb.py              # Database reader utility
├── inline-keyboard.py     # Inline keyboard utilities
├── test_tgb.py            # Tests for bot module
├── test_db_server.py      # Tests for Flask API
├── test_sandbox.py        # Sandbox tests
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── Makefile               # Build and test commands
├── .env.sample            # Environment variable template
└── README.md              # This file
```

## Testing

### Run tests with Docker

```bash
docker run --rm \
  -v $(pwd):/app -w /app \
  -e TELEGRAM_BOT_API_KEY=test \
  python:3.11-slim \
  bash -c "pip install --no-cache-dir -r requirements.txt && python -m pytest -v --tb=short"
```

### Run tests locally

```bash
pip install -r requirements.txt
TELEGRAM_BOT_API_KEY=test python -m pytest -v --tb=short
```

### Running specific test files

```bash
python -m pytest test_db_server.py -v --tb=short
python -m pytest test_tgb.py -v --tb=short
```

## License

This project is open source. See the LICENSE file for details.
