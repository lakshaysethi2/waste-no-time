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

cypress-run:
	docker compose build cypress
	docker compose --profile test up -d nginx api
	docker compose --profile test run --rm cypress
