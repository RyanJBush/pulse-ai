# Pulse AI Monorepo

Pulse AI is a production-oriented monorepo scaffold for a real-time anomaly detection platform.

## Stack
- **Backend:** FastAPI + SQLAlchemy
- **Frontend:** React + Vite scaffold with layout and pages
- **Database:** PostgreSQL
- **ML Layer:** Z-score + Isolation Forest anomaly detection
- **DevOps:** Docker Compose + GitHub Actions CI

## Features Implemented
- Event ingestion pipeline with persistence and structured logging.
- Hybrid anomaly detection using statistical Z-score and Isolation Forest.
- Anomaly scoring API for model-only scoring requests.
- Alert generation for anomalous events.
- Unit/API tests for ingestion, scoring, and alert generation.

## Repository Structure

```text
pulse-ai/
├── backend/
├── frontend/
├── docs/
├── .github/workflows/ci.yml
├── docker-compose.yml
└── Makefile
```

## Quick Start

### 1) Local (without Docker)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### 2) Docker Compose

```bash
make up
```

## Core API Endpoints
- `POST /api/v1/events/ingest`
- `GET /api/v1/events`
- `POST /api/v1/scoring/anomaly`
- `GET /api/v1/alerts`
- `GET /health`

## Test

```bash
cd backend
pytest -q
```

## Next Steps
- Add Alembic migrations and schema versioning.
- Add alert notification channels (Slack, PagerDuty, email).
- Add frontend views for scoring breakdown and alert triage.
- Add authn/authz and multi-tenant support.
