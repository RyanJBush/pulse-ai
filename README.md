# Pulse AI

Pulse AI is a production-style MVP monorepo for real-time anomaly detection. It ingests events, scores them with a blended Z-score + Isolation Forest approach, generates alerts, and exposes dashboards for monitoring.

## Monorepo layout

- `backend/` – FastAPI API, SQLAlchemy models, anomaly scoring logic, pytest + ruff setup
- `frontend/` – React + Vite + Tailwind + Recharts UI
- `docs/` – lightweight architecture documentation
- `.github/workflows/ci.yml` – GitHub Actions pipeline for backend/frontend linting, tests, and build

## Backend API

- `GET /health`
- `POST /api/events`
- `GET /api/events`
- `POST /api/anomaly/score`
- `GET /api/anomaly/{event_id}`
- `GET /api/alerts`
- `GET /api/alerts/{id}`
- `GET /api/metrics/summary`

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
