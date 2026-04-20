.PHONY: install backend-install frontend-install lint test up down

install: backend-install frontend-install

backend-install:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

frontend-install:
	cd frontend && npm install

lint:
	cd backend && . .venv/bin/activate && ruff check app
	cd frontend && npm run lint

test:
	cd backend && . .venv/bin/activate && pytest

up:
	docker compose up --build -d

down:
	docker compose down -v
