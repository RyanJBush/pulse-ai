# API Endpoints

## Events
- `POST /api/v1/events/ingest` - ingest a new event, score it, and conditionally create an alert.
- `GET /api/v1/events` - list recent events.

## Anomaly Scoring
- `POST /api/v1/scoring/anomaly` - run scoring on a payload without storing event data.

## Alerts
- `GET /api/v1/alerts` - list generated alerts.

## Health
- `GET /health` - basic liveness check.
