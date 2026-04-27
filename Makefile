.PHONY: backend-install frontend-install lint test build format demo-replay

backend-install:
	pip install -e ./backend[dev]

frontend-install:
	npm --prefix frontend install

lint:
	ruff check backend/app backend/tests
	npm --prefix frontend run lint
	npm --prefix frontend run format:check

test:
	PYTHONPATH=backend pytest backend/tests

build:
	npm --prefix frontend run build

format:
	ruff format backend/app backend/tests
	npm --prefix frontend run format

demo-replay:
	python backend/scripts/run_demo.py --base-url http://localhost:8000
