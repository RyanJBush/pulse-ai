# Orbit — Real-Time Anomaly Detection and Monitoring Platform

**Portfolio demo for anomaly detection workflows with a monitoring-style UI and API-first backend.**

Orbit is a recruiter-friendly project that shows how I design, build, and document an anomaly detection system from data ingest through alert and incident handling. It runs locally with Docker, uses seeded synthetic data, and focuses on transparent implementation choices instead of inflated production claims.

## Recruiter Summary

I am a **University of Maryland student studying Information Science and Electrical Engineering with a Business minor.** Orbit demonstrates practical full-stack engineering: FastAPI + PostgreSQL backend services, blended anomaly scoring, and a React dashboard for triage workflows. The project is a demo-scale system intended for portfolio review and technical discussion.

## What this project demonstrates

- Building and documenting a complete anomaly workflow: ingest → score → detect → triage.
- Blending multiple detection strategies (Z-score, Isolation Forest, rolling baseline, minute-bucket seasonal proxy).
- Creating operational workflows for alerts, incidents, and analyst notes.
- Designing APIs and data models with honest scope boundaries.
- Shipping a local developer experience with Docker Compose, Swagger docs, and repeatable seeded replay.

## What's Implemented vs. Planned

### ✅ Implemented in this repository

- ✅ FastAPI backend with REST endpoints for ingest, scoring, alerts, incidents, metrics, governance, and evaluation.
- ✅ PostgreSQL-backed persistence (with SQLite fallback for local experimentation).
- ✅ Replay engine that **simulates streaming ingestion** using deterministic seeded event generation.
- ✅ Blended scoring service (Z-score + Isolation Forest + rolling baseline + minute-bucket seasonal proxy).
- ✅ Alert lifecycle (open/acknowledged/resolved), incident grouping, and notes/audit tracking.
- ✅ React + Vite dashboard with KPI cards, anomaly trends, alerts table, and incident drawer.
- ✅ Local run path via Docker Compose and API docs via Swagger/OpenAPI.

### 🔲 Planned / future work

- 🔲 Real streaming ingestion infrastructure (Kafka/Kinesis/WebSocket ingestion path).
- 🔲 External alerting integrations (Slack, PagerDuty, email).
- 🔲 Full seasonal decomposition baselines beyond the current minute-bucket proxy.
- 🔲 Push-based UI updates (WebSocket/SSE) instead of REST polling.
- 🔲 Broader production observability posture (distributed tracing, multi-service SLO instrumentation).

## Tech stack

- **Backend:** FastAPI, SQLAlchemy 2.x, Pydantic, Python 3.11
- **Database:** PostgreSQL 16 (Docker), SQLite fallback
- **Detection/ML:** scikit-learn (Isolation Forest), Python statistical scoring
- **Frontend:** React, Vite, Tailwind CSS, Recharts
- **Tooling:** Docker Compose, pytest, ruff, ESLint, Prettier, GitHub Actions

## Architecture overview

- Pipeline stages: **Ingest → Model → Detect → Alert**
- Ingestion mode today: deterministic replay and API ingest (streaming-style architecture for demo use)
- Detection mode today: blended statistical + ML scoring
- Human workflow: alert triage, incident status updates, and notes

For deeper details, see [`docs/architecture.md`](docs/architecture.md) and [`docs/api.md`](docs/api.md).

## How to run locally

### Docker (recommended)

```bash
docker compose up --build
```

Then open:
- API docs: `http://localhost:8000/docs`
- UI (Portfolio Preview): `http://localhost:4173`

### Optional seeded demo replay

```bash
make demo-replay
# or
python backend/scripts/run_demo.py --count 200 --seed 77 --spike-every 10
```

## Demo workflow

1. Start the stack with Docker Compose.
2. Replay seeded events to populate activity and anomalies.
3. Open the UI to review KPI cards, trend behavior, alerts, and incidents.
4. Open Swagger docs to inspect endpoint coverage.
5. Review [`docs/observability.md`](docs/observability.md) for incident-style walkthroughs.

## Screenshots / demo

This repository includes captured UI/API screenshots in [`docs/screenshots/`](docs/screenshots/):
- `01-kpi-dashboard.png`
- `02-anomaly-trend-chart.png`
- `03-alerts-table.png`
- `04-incident-drawer.png`
- `05-api-docs.png`

See [`docs/screenshots/README.md`](docs/screenshots/README.md) for context and capture notes.

## Limitations and future work

- This is a **portfolio demo** using synthetic replayed data.
- No public hosted deployment is provided in this repository.
- No external paging/notifier integration is currently wired.
- Seasonal modeling is currently a proxy approach, not full decomposition.
- UI updates currently rely on polling rather than push streaming.

## Resume bullets

See [`docs/resume-bullets.md`](docs/resume-bullets.md).

## License

MIT (see [`LICENSE`](LICENSE)).
