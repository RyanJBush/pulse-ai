# Real-Time Anomaly Detection & Observability Platform

This repository contains a recruiter-ready demonstration platform focused on anomaly detection workflows for cloud engineering, SRE, DevOps, data engineering, and ML-oriented roles. It combines a FastAPI backend, PostgreSQL persistence, Prometheus instrumentation, and a React frontend to show how telemetry-like events can be ingested, scored, triaged as alerts, and tracked through incidents. The implementation is intentionally transparent: it provides production-inspired patterns while clearly separating what is implemented today from what is future work.

## Reliability/observability problem this project solves

Modern systems generate high-volume operational signals, but teams still struggle to turn noisy metric spikes into actionable incidents quickly. This project demonstrates a practical approach: apply multi-detector anomaly scoring, generate severity-tagged alerts, suppress duplicates, and expose incident workflows with notes/audit data so responders can triage faster and retain investigation context.

## Key features

- **Event ingestion and replay** via API routes and a seeded demo replay script for deterministic walkthroughs.
- **Multi-detector anomaly scoring** combining z-score, Isolation Forest, rolling baseline deviation, and a minute-bucket seasonal proxy.
- **Dynamic thresholding and explainability metadata** (reason codes, confidence, direction, baseline/deviation fields).
- **Alert lifecycle logic** with severity levels, cooldown suppression, and alert notes.
- **Incident lifecycle management** including status changes, incident notes, and audit-log style tracking in the data model.
- **Metrics and observability endpoints** with summary/entity metrics APIs plus Prometheus `/metrics` exposure.
- **Frontend operations views** for KPI cards, anomaly trend charting, alerts table triage, incidents, and events pages.
- **Evaluation/governance APIs** for threshold tuning, detector comparison, and detector configuration/suppression controls.

## Tech stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Pydantic
- **Detection/ML:** scikit-learn (Isolation Forest), NumPy, statistical scoring logic
- **Data stores:** PostgreSQL (Docker default), Redis service in compose stack
- **Observability instrumentation:** prometheus-fastapi-instrumentator, prometheus-client
- **Frontend:** React, Vite, Tailwind CSS, Recharts
- **Developer tooling:** Docker Compose, Makefile workflows, pytest, Ruff, ESLint, Prettier

## Anomaly detection workflow

1. **Ingest telemetry-like events** (`/api/v1/events`) or run seeded replay (`backend/scripts/run_demo.py`).
2. **Load contextual history** by source/workspace/signal/entity.
3. **Compute detector signals**:
   - z-score deviation from baseline,
   - Isolation Forest outlier score,
   - rolling percentile-window breach,
   - minute-bucket seasonal deviation proxy.
4. **Blend detector scores** with profile weights selected by signal type (or config override).
5. **Apply dynamic thresholding + hard checks** (e.g., large z-score / strong rolling breach).
6. **Persist scoring output** (combined score, confidence, reason codes, deviation metrics, explanation).
7. **Create/suppress alerts** based on threshold and cooldown rules.
8. **Drive incident workflows** through API + UI with notes and status updates.

## Observability and monitoring overview

Implemented observability capabilities in this repository include:

- **Health/readiness endpoints:** `/health` and `/ready`.
- **Prometheus metrics exposure:** `Instrumentator().instrument(app).expose(app)` enables a Prometheus-scrapable metrics endpoint.
- **Custom domain metrics objects:** counters/gauges/histograms for anomalies, active alerts, and model inference latency.
- **Request logging middleware:** request IDs and request duration logging for traceable API calls.
- **Operational UI monitoring surface:** dashboard KPI cards and trend tables powered by backend metrics/event APIs.

Not implemented in this repo today: real streaming bus ingestion, external paging/chat integrations, push-based live updates (WebSockets/SSE), or distributed tracing.

## Architecture overview

High-level implemented flow:

`React UI (polling API)` → `FastAPI routers` → `Scoring service` → `Alert service` → `Incident service` → `PostgreSQL`

Supporting platform components:

- **Redis** service in the Docker stack.
- **Prometheus** service configured via `prometheus.yml` to scrape backend metrics.
- **Background job runner** started at app lifespan startup.

The architecture is modular and interview-friendly: each phase (ingest, score, alert, incident, metrics/evaluation) is separated into routers, services, schemas, and models.

## Setup and installation

### Option A: One-command demo bootstrap

```bash
make dev-start
```

This builds/starts Docker services, waits for backend health, and runs seeded replay data.

### Option B: Manual Docker workflow

```bash
docker compose up --build
make demo-replay
```

### Local app URLs (default)

- Backend API docs: `http://localhost:8000/docs`
- Frontend UI: `http://localhost:4173`
- Prometheus UI: `http://localhost:9090`

### Useful development commands

```bash
make test
make lint
make build
```

## Example use cases

- **SRE interview demo:** show end-to-end path from anomaly signal to alert triage and incident note-taking.
- **Cloud/platform engineering portfolio:** discuss API reliability patterns (health/readiness, rate limiting, structured logs, metrics).
- **Data/ML engineering conversation:** explain how statistical and ML detectors are blended and tuned with evaluation endpoints.
- **DevOps workflow showcase:** run the local multi-service stack and validate API + UI + metrics integration in one environment.

## Skills demonstrated

- API design and backend architecture (FastAPI routers/services/models/schemas)
- Applied anomaly detection (statistical + unsupervised ML)
- Observability fundamentals (metrics exposure, request logging, health probes)
- Alert/incident workflow modeling (triage, suppression, state transitions, notes, audit records)
- Full-stack integration (React UI consuming operational APIs)
- Reproducible developer experience (Make + Docker Compose + tests/linting)

## Resume-ready project description

Built a full-stack anomaly detection and observability platform that ingests telemetry-like events, computes multi-detector anomaly scores (z-score, Isolation Forest, rolling baseline, seasonal proxy), and operationalizes results through alert triage and incident workflows. Implemented FastAPI services with PostgreSQL persistence, Prometheus-instrumented metrics endpoints, and a React dashboard for KPI/trend monitoring and investigation. Designed for interview-grade reliability engineering demonstrations with clear implemented-vs-future boundaries.

## Future improvements

- Add true streaming ingestion (e.g., Kafka/Kinesis/WebSocket path) instead of replay-simulated flow.
- Add external notification/integration targets (Slack/PagerDuty/email).
- Add push-based frontend updates (SSE/WebSocket) to reduce polling.
- Extend seasonality modeling beyond minute-bucket proxy (e.g., richer decomposition).
- Expand production-hardening patterns (distributed tracing, stronger auth, SLO-centric reporting).

