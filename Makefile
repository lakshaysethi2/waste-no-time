.PHONY: down logs up test lint clean backup

down:
	docker compose down

logs:
	docker compose logs -f

up:
	make down
	docker compose build
	docker compose up -d

test:
	python manage.py test

lint:
	@echo "Running flake8..."
	flake8 --max-line-length=120 --ignore=E302,E303,E305,E501,W291,W391 tracker/ waste_no_time/

backup:
	cp db.sqlite3 db.sqlite3.bak

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.db' -delete
	rm -rf .pytest_cache/
