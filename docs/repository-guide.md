# Repository Guide

This document gives a quick, code-oriented orientation for the Pulse AI monorepo.

## High-level layout

- `backend/`: FastAPI service for ingestion, anomaly scoring, alert/incident workflows, governance, and evaluation.
- `frontend/`: React + Vite operator UI for dashboards, events, alerts, metrics, and replay/evaluation workflows.
- `docs/`: architecture, API, deployment, demo, and this repository guide.

## Backend organization

- `app/main.py`: application startup/lifespan, middleware (request tracing + rate limiting), and health endpoints.
- `app/api/router.py`: top-level API router that mounts domain routers under `/api/v1`.
- `app/api/routers/*.py`: HTTP endpoints split by domain (`events`, `alerts`, `incidents`, `metrics`, `evaluation`, `governance`, `ai`, `scoring`).
- `app/services/*.py`: business logic invoked by routers.
- `app/models/*.py`: SQLAlchemy ORM models.
- `app/schemas/*.py`: request/response models.
- `app/core/*.py`: shared runtime components (`config`, logging, auth, cache, background jobs, ingestion buffer).
- `app/anomaly.py`: anomaly scoring implementation.
- `tests/`: pytest suite covering API flows and phased feature behavior.

## Frontend organization

- `src/main.jsx`: entrypoint that mounts the app.
- `src/App.jsx`: main UI container currently holding most page/workflow logic.
- `src/pages/`: page-level components (Dashboard, Events, Alerts, Metrics).
- `src/components/`: reusable visual/UX components.
- `src/services/api.js`: lightweight API wrappers.

## Runtime and tooling

- Backend stack: Python, FastAPI, SQLAlchemy, Pydantic settings, scikit-learn + NumPy.
- Frontend stack: React, Vite, Tailwind, Recharts.
- Local orchestration: `docker-compose.yml` starts Postgres + backend + frontend.
- Quality: pytest-based tests and frontend lint/build scripts.
