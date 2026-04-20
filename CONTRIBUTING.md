# Contributing

## Development setup
1. Copy environment variables as needed (`DATABASE_URL` for backend).
2. Install backend deps: `pip install -e ./backend[dev]`
3. Install frontend deps: `cd frontend && npm install`

## Workflow
- Run `make lint` and `make test` before opening a PR.
- Keep changes scoped to the issue and include tests for backend behavior changes.
- Prefer small, reviewable commits.
