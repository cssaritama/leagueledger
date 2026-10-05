.PHONY: test backend-test frontend-check up down build smoke

test: backend-test frontend-check

backend-test:
	cd backend && uv sync && uv run ruff check app tests && uv run pytest -q

frontend-check:
	cd frontend && npm ci && npm run lint && npm run build

build:
	docker compose build

up:
	docker compose up --build -d --wait

down:
	docker compose down

smoke:
	./scripts/smoke-test.sh
