# Orbit — Portfolio-Scale Anomaly Detection Demo

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Open-22c55e?logo=render&logoColor=white)](https://anomaly-detection.onrender.com)

Orbit is a **portfolio-scale anomaly detection demo** that showcases a monitoring-style workflow: ingest signals, score anomalies, triage alerts, and review incidents. It is intentionally scoped for local development and interview walkthroughs rather than production observability operations.

## Academic identity

Built by a **University of Maryland student studying Information Science and Electrical Engineering with a Business minor.**

## What Orbit demonstrates

- Practical backend pipeline design for anomaly detection on synthetic telemetry-like signals.
- Transparent blending of statistical and ML-based anomaly scoring.
- Monitoring-inspired UI patterns (KPI cards, trend views, alert triage, incident review).
- Honest engineering communication with explicit implemented vs planned boundaries.

## What’s Implemented vs Planned

### ✅ Implemented in this repo

- ✅ FastAPI backend with endpoints for ingest, replay, scored events, metrics summaries, alerts, incidents, and evaluation.
- ✅ Deterministic replay flow that simulates streaming-like event arrival using seeded synthetic data.
- ✅ Blended anomaly scoring logic combining:
  - Z-score deviation checks,
  - Isolation Forest outlier scoring,
  - rolling baseline deviation,
  - minute-bucket seasonal proxy behavior.
- ✅ React dashboard experience for KPI overview, anomaly trend charting, alerts table, and incident drawer workflow.
- ✅ Local-first developer experience with Docker Compose and Swagger/OpenAPI docs.

### 🔲 Planned (not fully implemented yet)

- 🔲 Real streaming infrastructure (Kafka/Kinesis/WebSocket ingestion path).
- 🔲 External notification integrations (Slack, PagerDuty, email).
- 🔲 Push-based UI updates (WebSocket/SSE instead of polling).
- 🔲 More advanced seasonality/decomposition beyond current proxy method.
- 🔲 Production-grade observability hardening (multi-service tracing, SLO instrumentation, on-call integration).

## Tech stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic, Python 3.11
- **Database:** PostgreSQL (default in Docker) with SQLite fallback
- **Detection:** scikit-learn (Isolation Forest) + Python statistical logic
- **Frontend:** React, Vite, Tailwind CSS, Recharts
- **Tooling:** Docker Compose, Make, pytest, Ruff, ESLint, Prettier

## Monitoring Stack

Orbit uses **Prometheus + a custom React dashboard** for observability-style monitoring:

- **Prometheus** is used for backend instrumentation and metric scraping (`/metrics`) to track anomaly scoring, alert behavior, and service health.
- **Custom dashboards (implemented in the frontend app)** are used instead of Grafana for this portfolio project so the full user workflow (metrics view, anomalies, triage, incidents) can be demonstrated in one cohesive UI and codebase.

### Why custom dashboards instead of Grafana (for now)

- Better for interview demos: one URL, one UI, one narrative.
- Easier to tailor views to anomaly triage-specific fields and workflows.
- Tradeoff: less out-of-the-box paneling/alert-routing capability than a full Grafana stack.

If you adapt this project toward production observability operations, a typical next step is adding Grafana dashboards on top of Prometheus while keeping the app UI for incident-specific workflows.

## Anomaly Detection Methods

| Method | Algorithm | Use Case | Threshold Type |
| --- | --- | --- | --- |
| Z-Score | Rolling z-score over metric windows | Detect short-term statistical deviations from local baseline | Dynamic |
| Isolation Forest | Tree-based unsupervised outlier detection | Capture nonlinear and multivariate anomalous patterns | Dynamic |
| Baseline Deviation | Rolling mean/variance delta checks | Track drift or sudden departures from expected operating range | Statistical |
| Seasonal Proxy | Minute-bucket seasonal comparison | Flag metric spikes relative to recurring time-bucket behavior | Dynamic |

## Architecture (demo scope)

Pipeline stages:

1. **Ingest** — API ingest or deterministic replay-generated events.
2. **Analyze** — feature extraction / score component calculations.
3. **Detect** — blended anomaly score and anomaly flag decision.
4. **Alert** — alert creation + incident triage workflow in the UI.

This structure is observability-inspired, but currently implemented as a local portfolio demo with synthetic inputs.

## Alert Flow

```text
Metric Ingestion
  → Feature Extraction
  → ML Scoring
  → Threshold Evaluation
  → Alert
  → Dashboard/Notification
```

## One-command dev start

```bash
make dev-start
```

This command:

1. Builds/starts services with Docker Compose.
2. Waits for API health.
3. Runs seeded replay to populate sample anomalies.

### Manual run option

```bash
docker compose up --build
make demo-replay
```

## Demo workflow

1. Run `make dev-start`.
2. Open API docs at `http://localhost:8000/docs`.
3. Open the **Portfolio Preview UI** at `http://localhost:4173`.
4. Inspect anomaly trends, alerts, and incidents.
5. Optionally rerun replay with custom parameters:

```bash
python backend/scripts/run_demo.py --count 200 --seed 77 --spike-every 10
```

## Screenshots

Add images under `docs/images/` as the project evolves:

![Dashboard Overview](docs/images/dashboard-overview.png)
![Anomaly Trend View](docs/images/anomaly-trend.png)
![Alert Triage Table](docs/images/alerts-table.png)
![Incident Drilldown](docs/images/incident-drilldown.png)

## Limitations and future work

- Uses synthetic replay data rather than real production telemetry.
- Streaming behavior is simulated through replay, not a durable stream processor.
- External paging/notification tools are not wired yet.
- UI updates are polling-based today.
- Alert quality and thresholds are tuned for demo clarity, not production SLAs.

## Repository metadata (GitHub topics)

If applicable, manually add these GitHub repository topics for discoverability:

- `prometheus`
- `grafana`
- `observability`
- `alerting`

## Resume bullets

See [`docs/resume-bullets.md`](docs/resume-bullets.md) for portfolio and ATS-oriented bullet points.

## Related docs

- Architecture: [`docs/architecture.md`](docs/architecture.md)
- API reference: [`docs/api.md`](docs/api.md)
- Demo runbook: [`docs/demo-runbook.md`](docs/demo-runbook.md)
- Local change log: [`docs/change-log.md`](docs/change-log.md)
