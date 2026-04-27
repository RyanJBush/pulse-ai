# Pulse AI

Pulse AI is a production-style anomaly detection and monitoring platform with:

- real-time event ingestion,
- multi-detector scoring (z-score, isolation, rolling, seasonal),
- alert and incident workflows,
- replay/evaluation tooling for detector tuning.

---

## Repository layout

- `backend/` — FastAPI service, SQLAlchemy models, scoring/evaluation logic, pytest/ruff.
- `frontend/` — React + Vite operator console.
- `docs/` — architecture/API/deployment/demo docs.
- `.github/workflows/ci.yml` — CI for lint, tests, formatting, frontend build.

---

## API highlights

- Health: `GET /health`, `GET /ready`
- Events:
  - `POST /api/v1/events/ingest`
  - `GET /api/v1/events`
  - `GET /api/v1/events/scored`
  - `POST /api/v1/events/replay`
  - `POST /api/v1/events/buffer/enqueue`
  - `POST /api/v1/events/buffer/flush`
  - `GET /api/v1/events/buffer/stats`
- Alerts:
  - `GET /api/v1/alerts`
  - `PATCH /api/v1/alerts/{id}/status`
  - `POST /api/v1/alerts/{id}/notes`
  - `GET /api/v1/alerts/{id}/notes`
- Incidents:
  - `GET /api/v1/incidents`
  - `PATCH /api/v1/incidents/{id}`
  - `POST /api/v1/incidents/{id}/notes`
  - `GET /api/v1/incidents/{id}/notes`
- Metrics:
  - `GET /api/v1/metrics/summary`
  - `GET /api/v1/metrics/entities/{entity_id}`
- Evaluation:
  - `POST /api/v1/evaluation/seeded-benchmark`
  - `POST /api/v1/evaluation/threshold-tuning`
  - `POST /api/v1/evaluation/detector-comparison`

---

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

Set `VITE_API_BASE_URL` if backend is not running on `http://localhost:8000`.

---

## Docker Compose

```bash
docker compose up --build
```

Services:

- Postgres: `localhost:5432`
- Backend: `localhost:8000`
- Frontend: `localhost:4173`

---

## Demo runbook (Phase 5)

1. Start backend/frontend (or `docker compose up --build`).
2. Run synthetic replay demo:

```bash
make demo-replay
```

This script triggers replay and prints:

- replay metadata (`replay_run_id`, duration),
- latest KPI summary,
- latest anomalous scored events.

You can also run custom parameters:

```bash
python backend/scripts/run_demo.py --count 200 --seed 77 --spike-every 10
```

---

## Quality checks

```bash
make lint
make test
make build
```

---

## Additional docs

- API details: `docs/api.md`
- Architecture notes: `docs/architecture.md`
- Deployment guide: `docs/deployment.md`
- Demo walkthrough: `docs/demo.md`
