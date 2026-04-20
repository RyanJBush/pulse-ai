# Pulse AI

Pulse AI is a production-style MVP monorepo for real-time anomaly detection. It ingests events, scores them with a blended Z-score + Isolation Forest approach, generates alerts, and exposes dashboards for monitoring.

## Monorepo layout

- `backend/` – FastAPI API, SQLAlchemy models, anomaly scoring logic, pytest + ruff setup
- `frontend/` – React + Vite + Tailwind + Recharts UI
- `docs/` – lightweight architecture documentation
- `.github/workflows/ci.yml` – GitHub Actions pipeline for backend/frontend linting, tests, and build

## Backend API

- `GET /health`
- `GET /ready`
- `POST /api/v1/events/ingest`
- `GET /api/v1/events`
- `POST /api/v1/events/replay`
- `POST /api/v1/scoring/anomaly`
- `GET /api/v1/alerts`
- `PATCH /api/v1/alerts/{id}/status`
- `POST /api/v1/alerts/{id}/notes`
- `GET /api/v1/metrics/summary`
- `GET /api/v1/metrics/entities/{entity_id}`

Data model tables:
- `events`
- `anomaly_scores`
- `alerts`

## Local development

### Backend

```bash
pip install -e ./backend[dev]
uvicorn app.main:app --app-dir backend --reload
```

### Frontend

```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

Set `VITE_API_BASE_URL` if the backend is not on `http://localhost:8000`.

## Docker compose

```bash
docker compose up --build
```

Services:
- Postgres: `localhost:5432`
- Backend API: `localhost:8000`
- Frontend: `localhost:4173`

## Quality checks

```bash
make lint
make test
make build
```
