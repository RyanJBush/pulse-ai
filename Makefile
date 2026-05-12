.PHONY: backend-install frontend-install lint test build format demo-replay dev-start

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


dev-start:
	docker compose up -d --build
	@echo "Waiting for API health at http://localhost:8000/health ..."
	@for i in $$(seq 1 30); do \
		if curl -fsS http://localhost:8000/health >/dev/null; then \
			echo "API is healthy."; \
			break; \
		fi; \
		sleep 2; \
	done
	python backend/scripts/run_demo.py --base-url http://localhost:8000
