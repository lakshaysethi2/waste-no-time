.PHONY: up down build test test-live logs backup clean

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

test:
	docker compose exec web python manage.py test

test-live:
	# Run tests that interact with live Telegram API
	# Requires TELEGRAM_BOT_API_KEY to be set in .env.local
	docker compose exec web python manage.py test --tag=live

logs:
	docker compose logs -f

backup:
	mkdir -p backups
	cp db.sqlite3 backups/db.sqlite3.$$(date +%Y%m%d%H%M%S).bak

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache/
