.PHONY: backend-install frontend-install lint test build format

backend-install:
	pip install -e ./backend[dev]

frontend-install:
	npm --prefix frontend install

lint:
	ruff check backend/app backend/tests
	npm --prefix frontend run lint
	npm --prefix frontend run format:check

test:
	pytest backend/tests

build:
	npm --prefix frontend run build

format:
	ruff format backend/app backend/tests
	npm --prefix frontend run format
