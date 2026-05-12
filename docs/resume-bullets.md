# Resume Bullets — Orbit / Real-Time Anomaly Detection & Monitoring Platform

Concise, ATS-friendly bullets tuned for cloud / SRE / data-engineering / backend / ML roles.
Pick 3–5 that match each job description. Every bullet is verifiable against this repo —
file paths cited where useful — and avoids claims of production deployment, real users, or
paid incident response. Honest scope: this is a portfolio project, not a deployed system.

---

## Top picks — 8 ATS-friendly bullets

Use these as a default set. They cover the four dimensions a reviewer cares about: scope,
ML, reliability, and delivery.

- **Designed and shipped 34 REST endpoints across 9 FastAPI routers** for event ingestion, scoring, alerts, incidents, evaluation, metrics, governance, AI summaries, and model serving, fully documented via OpenAPI / Swagger UI (`backend/app/api/routers/`).
- **Built a blended anomaly detector in Python** combining Z-score, scikit-learn Isolation Forest, rolling-window, and a minute-bucket seasonal proxy into a single 0–1 confidence score with per-signal weight profiles (`backend/app/services/scoring_service.py`).
- **Modeled a 10-table normalized PostgreSQL schema in SQLAlchemy 2.0** for events, anomaly scores, alerts, alert notes, incidents, incident notes, detector configs, suppression rules, and an audit log capturing every alert/incident state transition.
- **Implemented a deterministic seeded-replay engine** and a threshold-tuning endpoint that emits precision / recall / FPR per threshold, so detector behavior is empirically measurable and reproducible across runs.
- **Engineered an alert lifecycle with per-source cooldown suppression**, alert→incident grouping, analyst notes, and an append-only audit log — patterns modeled on production SRE tooling.
- **Built a React + Vite + Tailwind + Recharts operator dashboard** wired to the live FastAPI backend, exposing latency / error-rate / throughput / anomaly-rate KPIs plus per-entity drill-down trends.
- **Containerized the full stack** (Postgres 16 + FastAPI + frontend) with Docker Compose for one-command local boot, and wired GitHub Actions CI to run ruff, 40 pytest tests, and a frontend production build on every push.
- **Added structured request/response logging with propagated request IDs**, in-process per-client rate limiting, and Kubernetes-style `/health` + `/ready` probes — the standard observability and reliability primitives.

---

## Long-form variants by role

### Anomaly detection & ML

- Built a blended anomaly detector combining Z-score, scikit-learn Isolation Forest, rolling-window, and a minute-bucket seasonal proxy into a single confidence score persisted per event, with per-signal weight profiles (latency / cpu / memory / error_rate / default).
- Implemented threshold-tuning and detector-comparison endpoints that run seeded benchmark replays and report precision, recall, and false-positive rate per detector and per threshold.
- Designed a deterministic replay engine that injects configurable-cadence spikes into synthetic event streams (seeded RNG) so detection tuning is reproducible across runs and across collaborators.

### Observability & monitoring (SRE-flavored)

- Engineered a FastAPI metrics service exposing latency, throughput, anomaly-rate, severity breakdown, and per-entity drill-down KPIs consumed by a React + Recharts operator dashboard.
- Modeled an alert + incident lifecycle (status transitions, analyst notes, alert→incident grouping, append-only audit log) in SQLAlchemy 2.0 with REST endpoints for status updates and note appending.
- Implemented alert suppression rules and per-source cooldown windows (configurable via `ALERT_COOLDOWN_SECONDS`) to reduce alert noise — a standard SRE pattern for keeping signal-to-noise high on production monitors.
- Added structured request/response logging with propagated request IDs, in-process per-client rate limiting, and `/health` + `/ready` probes to support standard observability and Kubernetes-style deployment patterns.
- Wrote incident-style runbook examples in `docs/observability.md` describing how Orbit surfaces a latency spike, an error-rate regression, and a throughput drop end-to-end (event → score → alert → incident).

### Data / streaming pipeline

- Built an ingestion pipeline with an in-process buffer that batches incoming events, scores them with a multi-detector pipeline, and conditionally emits alerts under a cooldown window to suppress duplicates.
- Implemented a deterministic event-replay simulator (configurable count, seed, spike interval) for benchmarking detector behavior on time-series data without depending on external data sources.
- Modeled time-series events, anomaly scores, alerts, incidents, suppression rules, and audit logs in a normalized PostgreSQL 16 schema with SQLAlchemy 2.0.

### APIs & backend engineering

- Designed and shipped 34 REST endpoints in FastAPI covering ingestion, scoring, alerts, incidents, evaluation, metrics, governance, AI summary, and model serving, documented via OpenAPI / Swagger UI.
- Added a header-based role guard (`X-Role`: admin / operator / analyst / viewer) on governance, evaluation, incident, and AI routes — note: this is a portfolio-grade gate, not OAuth.
- Wrote 40 pytest tests covering ingestion, scoring math, alert generation, evaluation metrics, and API contracts, wired into GitHub Actions CI on every push so regressions are caught before merge.
- Containerized backend, frontend, and Postgres with a single `docker compose up` to give reviewers a one-command local stack.

### Frontend / full-stack

- Built a React + Vite + Tailwind + Recharts operator dashboard with KPI cards, entity drill-down trend charts, an alerts table, and an incident drawer — all driven by REST polling against the live FastAPI backend.
- Wired ESLint + Prettier and a frontend production build into CI so layout regressions and lint drift are caught before merge.

---

## Tailoring tips

- **SRE / observability roles:** lead with alert lifecycle, suppression / cooldown, latency / error-rate / throughput KPIs, and the audit log.
- **Data engineering roles:** lead with the deterministic replay engine, time-series schema, and detector evaluation tooling.
- **Applied ML / ML platform roles:** lead with blended scoring, per-signal weight profiles, threshold tuning, and the precision/recall evaluation endpoints.
- **Backend / API roles:** lead with FastAPI surface area, OpenAPI docs, SQLAlchemy modeling, CI test coverage, and the request-id / rate-limit middleware.
- **Full-stack roles:** lead with the React + Recharts dashboard wired to the live API, Docker Compose stack, and end-to-end CI.

---

## Honest scope (keep this disclosure visible)

This is a portfolio project. It is **not** deployed to production, has no real users, and
does not handle real on-call paging. The "incidents" are simulated against replayed
synthetic streams. Bullets above are phrased to reflect that — "engineered," "built,"
"designed," "shipped" — rather than implying live operational ownership or paid impact.

Also note these scope boundaries (matching the [README Limitations table](../README.md#-limitations--future-work)):

- Auth is a portfolio-grade `X-Role` header gate, not OAuth / JWT / sessions.
- Streaming transport (Kafka / NATS / Kinesis) is not implemented; ingestion is REST-only.
- Throughput-floor / silent-failure alerts are planned, not implemented.
- The seasonal baseline is a minute-bucket proxy; full Fourier/STL decomposition is planned.
- No external alerting integrations (Slack / PagerDuty / email) exist today.

If asked about any of the above in an interview, the honest answer is "that's on the
roadmap — here's the seam where it would plug in" rather than overclaiming.
