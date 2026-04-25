# API Endpoints

## Events
- `POST /api/v1/events/ingest` - ingest a new event, score it, and conditionally create an alert.
- `GET /api/v1/events` - list recent events.
- `GET /api/v1/events/scored` - list recent events joined with latest scoring rationale and alert linkage.
- `POST /api/v1/events/replay` - replay seeded synthetic streams with configurable spikes/out-of-order behavior.

## Anomaly Scoring
- `POST /api/v1/scoring/anomaly` - run multi-detector scoring on a payload without storing event data.

## Alerts
- `GET /api/v1/alerts` - list generated alerts.
- `PATCH /api/v1/alerts/{alert_id}/status` - update alert lifecycle status.
- `POST /api/v1/alerts/{alert_id}/notes` - append investigation notes.
- `GET /api/v1/alerts/{alert_id}/notes` - list alert notes.

## Metrics
- `GET /api/v1/metrics/summary` - KPI summary (anomaly rate, throughput, alert count, severity/latency stats).
- `GET /api/v1/metrics/entities/{entity_id}` - entity drill-down metrics.

## Health
- `GET /health` - basic liveness check.
- `GET /ready` - readiness check.
