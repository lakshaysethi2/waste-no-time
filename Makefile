.PHONY: down logs up up-low-logs up-verbose-logs test test-verbose lint clean

down:
	docker compose down

logs:
	docker compose logs -f

up:
	make down
	docker compose build
	docker compose up -d

up-low-logs:
	make down
	docker compose build api > /dev/null 2>&1
	LOG_LEVEL=low docker compose up -d
	docker compose logs --tail=10 api

up-verbose-logs:
	make down
	docker compose build api
	LOG_LEVEL=verbose docker compose up -d
	docker compose logs -f api

test:
	docker compose build api > /dev/null 2>&1
	docker compose up -d > /dev/null 2>&1
	docker compose exec api npm run test:extended
	docker compose exec api npm test

test-verbose:
	docker compose build api
	docker compose up -d
	docker compose exec api npm run test:extended
	docker compose exec api npm test

lint:
	@echo "Running flake8..."
	-pip install flake8 2>/dev/null
	-flake8 --max-line-length=120 --ignore=E302,E303,E305,E501,W291,W391 main.py manictime.py db_server.py keyvalue.py variables.py

test-python:
	docker run --rm \
		-v $(PWD):/app -w /app \
		-e TELEGRAM_BOT_API_KEY=test \
		python:3.11-slim \
		bash -c "pip install --no-cache-dir -r requirements.txt && python -m pytest -v --tb=short"

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.db' -delete
	rm -rf .pytest_cache/
