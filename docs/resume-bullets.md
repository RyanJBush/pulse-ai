# Resume Bullets — Orbit / Real-Time Anomaly Detection & Monitoring Platform

Concise, ATS-friendly bullets tuned for cloud / SRE / data-engineering roles. Pick 3–5 that
best match each job description. All bullets describe work actually present in this repo and
avoid claims of production deployment, real users, or paid incident response.

---

## Anomaly detection & ML

- Built a blended anomaly detector in Python that combines Z-score, scikit-learn Isolation Forest, rolling mean, and seasonal baselines into a single confidence score persisted per event.
- Implemented threshold-tuning and detector-comparison endpoints that run seeded benchmark replays and report precision, recall, and false-positive rate per detector.
- Designed a replay engine that injects deterministic spikes into synthetic event streams (seeded random) so detection tuning is reproducible across runs.

## Observability & monitoring

- Engineered a FastAPI metrics service exposing latency, throughput, anomaly-rate, severity breakdown, and per-entity drill-down KPIs consumed by a React + Recharts operator dashboard.
- Modeled an alert + incident lifecycle (status transitions, analyst notes, alert→incident grouping) in SQLAlchemy with REST endpoints for status updates and note appending.
- Added structured request/response logging and `/health` + `/ready` probes to support standard observability patterns (liveness, readiness, structured logs).

## Data / streaming pipeline

- Built an ingestion pipeline that buffers incoming events, scores them with a multi-detector pipeline, and conditionally emits alerts under a cooldown window to suppress duplicates.
- Implemented a deterministic event-replay simulator (configurable count, seed, spike interval) for benchmarking detector behavior on time-series data without depending on external data sources.
- Modeled time-series events, anomaly scores, alerts, incidents, suppression rules, and audit logs in a normalized PostgreSQL schema with SQLAlchemy 2.0.

## APIs & backend engineering

- Designed and shipped 25+ REST endpoints in FastAPI covering ingestion, scoring, alerts, incidents, evaluation, metrics, and governance, documented via OpenAPI / Swagger UI.
- Added pytest test suites (40+ tests) covering ingestion, scoring math, alert generation, evaluation metrics, and API contracts, wired into GitHub Actions CI on every push.
- Containerized backend, frontend, and Postgres with a single `docker compose up` command to give reviewers a one-command local stack.

## Reliability / SRE-flavored

- Implemented alert suppression rules and per-source cooldown windows to reduce alert noise — a common SRE pattern for keeping signal-to-noise high on production-style monitors.
- Wrote incident-style runbook examples in `docs/` describing how Orbit would surface a latency spike, an error-rate regression, and a throughput drop end-to-end (event → score → alert → incident).
- Added GitHub Actions CI running ruff lint, pytest, and a frontend production build on every push so regressions are caught before merge.

---

## Tailoring tips

- For **SRE / observability** roles: lead with alert lifecycle, suppression, latency/error-rate/throughput KPIs, and the incident workflow.
- For **data engineering** roles: lead with the streaming/replay pipeline, time-series schema, and detector evaluation tooling.
- For **ML / applied ML** roles: lead with the blended scoring approach, threshold tuning, and precision/recall evaluation endpoints.
- For **backend / API** roles: lead with FastAPI surface area, OpenAPI docs, SQLAlchemy modeling, and CI test coverage.

## Honest scope

This is a portfolio project. It is **not** deployed to production, has no real users, and does
not handle real on-call paging. The "incidents" are simulated against replayed synthetic
streams. Bullets above are phrased to reflect that — "engineered," "built," "designed" —
rather than implying live operational ownership.
