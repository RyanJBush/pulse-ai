# Orbit — API Documentation (Portfolio Demo Scope)

Base prefix: `/api/v1`.
Swagger UI: `http://localhost:8000/docs`.

This API supports a **local demonstrator** for anomaly detection + monitoring operations. It is not a production multi-tenant control plane.

## What the API demonstrates

- Event ingestion and deterministic replay.
- Multi-detector anomaly scoring.
- Alert triage (status + notes).
- Incident workflow (status + notes).
- Metrics and trend retrieval for dashboard visualization.
- Evaluation/governance endpoints for detector tuning.

## Scope guardrails (accuracy)

- Auth is **header role-gating** (`X-Role`) on selected routes, not OAuth/JWT/session auth.
- UI updates are driven by REST polling; no WebSocket/SSE stream contract is exposed.
- No outbound Slack/PagerDuty/email integration endpoints.
- Seasonal baseline logic is a proxy heuristic in scoring, not full seasonal decomposition.

## Route groups

- `/events`: ingest, replay, buffered ingestion utilities, scored-event listing.
- `/scoring`: on-demand anomaly scoring.
- `/alerts`: list, status transitions, notes.
- `/incidents` (role-gated): list, status transitions, notes.
- `/metrics`: summary + per-entity trend queries.
- `/evaluation` (role-gated): seeded benchmark, threshold tuning, detector comparison.
- `/governance` (role-gated): detector configs, suppression rules, audit logs.
- `/ai` (role-gated): summary endpoints for anomaly/incident narratives.
- `/serving`: prediction + serving health.

For exact request/response schemas and current endpoint list, treat the generated OpenAPI docs (`/docs`, `/openapi.json`) as source of truth.
