# Orbit — REST API Reference

All endpoints are prefixed with `API_PREFIX` (default `/api/v1`). Interactive Swagger UI is
served at [`http://localhost:8000/docs`](http://localhost:8000/docs) once the backend is up.

## Conventions

- **Content type:** JSON for all request and response bodies.
- **Auth:** routes marked 🔒 require an `X-Role` header. Allowed values: `admin`,
  `operator`, `analyst`, `viewer`. Per-route role sets are listed below. The guard lives in
  [`app/core/auth.py`](../backend/app/core/auth.py). There is **no** OAuth, JWT, or session
  auth — see the [Limitations table](../README.md#-limitations--future-work).
- **Request IDs:** the server accepts an optional `x-request-id` header and echoes it on
  the response. If missing, a UUID v4 is generated and logged.
- **Rate limit:** per-client minute-bucket cap from `RATE_LIMIT_PER_MINUTE` (default 240).
  Over-limit requests get `429 rate limit exceeded`.
- **Status codes:** `201` for created resources, `200` for reads, `202` for buffered
  ingest, `400`/`403`/`404`/`429` for the expected error cases.

## Health

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness probe — always 200 if the process is up. |
| `GET` | `/ready` | Readiness probe — 200 once the DB session can be acquired. |

## Events (`/api/v1/events`)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/ingest` | Ingest one event, score it, and conditionally create an alert. |
| `GET`  | `` | List recent events (`limit`, `offset`, `sort_desc`, `workspace_id`). |
| `POST` | `/replay` | Replay a seeded synthetic stream (`count`, `seed`, `inject_spike_every`). Deterministic. |
| `GET`  | `/scored` | List events joined with their latest score and any linked alert. `anomalous_only=true` filters to flagged events. |
| `POST` | `/buffer/enqueue` | Enqueue an event into the in-process ingestion buffer (`202` accepted). |
| `POST` | `/buffer/flush` | Flush buffered events into the scoring pipeline. |
| `GET`  | `/buffer/stats` | Buffer health: queued / enqueued / flushed counters. |
| `POST` | `/simulation/start` | Kick off a deterministic simulation run. |
| `POST` | `/simulation/inject-anomaly` | Inject a single anomalous event into an in-flight simulation. |

## Scoring (`/api/v1/scoring`)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/anomaly` | Run multi-detector scoring on a payload **without** persisting an event — useful for ad-hoc inspection. |

## Alerts (`/api/v1/alerts`)

| Method | Path | Purpose |
|---|---|---|
| `GET`   | `` | List alerts with filters (severity, status, source, etc.). |
| `PATCH` | `/{alert_id}/status` | Transition alert lifecycle (`open` → `acknowledged` → `resolved`). |
| `POST`  | `/{alert_id}/notes` | Append an investigation note. |
| `GET`   | `/{alert_id}/notes` | List notes for an alert. |

## Incidents (`/api/v1/incidents`) 🔒

All incident routes require a role header (analyst+ for reads, operator+ for writes).

| Method | Path | Purpose |
|---|---|---|
| `GET`   | `` | List incidents (analyst, operator, admin). |
| `PATCH` | `/{incident_id}/status` | Transition incident status (operator, admin). |
| `POST`  | `/{incident_id}/notes` | Append an incident note (analyst, operator, admin). |
| `GET`   | `/{incident_id}/notes` | List notes for an incident (analyst, operator, admin). |

## Metrics (`/api/v1/metrics`)

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/summary` | KPI summary — anomaly rate, throughput, severity mix, latency stats. |
| `GET` | `/entities/{entity_id}` | Per-entity drill-down metrics. |
| `GET` | `/entities/{entity_id}/trends` | Time-bucketed trend series for one entity (used by the dashboard line chart). |

## Evaluation (`/api/v1/evaluation`) 🔒

All evaluation routes require analyst+ role.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/seeded-benchmark` | Run a seeded labeled replay and return precision / recall / FPR. |
| `POST` | `/threshold-tuning` | Sweep thresholds against the benchmark; returns per-threshold metrics + recommended threshold. |
| `POST` | `/detector-comparison` | Compare detector TPR / FPR on a selected data slice. |

## Governance (`/api/v1/governance`) 🔒

| Method | Path | Roles | Purpose |
|---|---|---|---|
| `GET`  | `/detectors` | admin, operator, analyst | List per-signal detector configs (weights, enabled flag). |
| `PUT`  | `/detectors` | admin, operator | Upsert a detector config (override default weight profile). |
| `GET`  | `/audit-logs` | admin, operator, analyst | Audit log of state transitions (alerts, incidents, configs). |
| `POST` | `/suppression-rules` | admin, operator | Add a suppression rule for `(source, signal_type)`. |
| `GET`  | `/suppression-rules` | admin, operator, analyst | List suppression rules (filterable by `workspace_id`). |

## AI Summaries (`/api/v1/ai`) 🔒

| Method | Path | Roles | Purpose |
|---|---|---|---|
| `GET` | `/anomalies/{anomaly_score_id}/summary` | admin, operator, analyst | Plain-language summary of an anomaly score's drivers. |
| `GET` | `/daily-briefing` | admin, operator, analyst, viewer | Aggregated daily briefing (defaults to today UTC). |
| `GET` | `/incidents/{incident_id}/wrap-up` | admin, operator, analyst | Post-incident wrap-up summary. |

## Model Serving (`/api/v1/serving` and `/serving`)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/predict` | Synchronous prediction over a feature payload — used by the dashboard ad-hoc tester. |
| `GET`  | `/health` | Serving subsystem health. |

> The serving router is mounted at both `/api/v1/serving` and `/serving` (see
> `backend/app/api/router.py`) so the model-serving subsystem can be reached without the
> versioned prefix.

## Total

- **9 routers · 34 endpoints** (excluding `/health` and `/ready`).
- Verified with `grep -c "@router\." backend/app/api/routers/*.py`.

## Examples

See [`README.md → API Examples`](../README.md#-api-examples) for ready-to-paste `curl`
snippets covering ingest, replay, KPI summary, anomalous-event listing, and
threshold-tuning.

## OpenAPI / Swagger

The canonical machine-readable contract is generated by FastAPI:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- JSON: `http://localhost:8000/openapi.json`

If this Markdown reference and the OpenAPI document diverge, **the OpenAPI document is
authoritative** — it's generated directly from the running code.
