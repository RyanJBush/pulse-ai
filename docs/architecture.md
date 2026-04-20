# Architecture Overview

Pulse AI is organized as a monorepo with clear domain boundaries:

- **backend/**: FastAPI API layer, business services, SQLAlchemy models.
- **frontend/**: React dashboard for monitoring events and alerts.
- **PostgreSQL**: Primary transactional store for events, anomaly scores, and alerts.
- **ML Detection Layer**: Z-score + Isolation Forest scoring service.

## Runtime Flow
1. Client sends event to `POST /api/v1/events/ingest`.
2. Event is persisted in `events` table.
3. Scoring service calculates Z-score and Isolation Forest score from historical values.
4. Combined anomaly score is computed and stored in `anomaly_scores`.
5. If event is anomalous, an alert is written to `alerts`.
6. Frontend consumes `events` and `alerts` APIs to render dashboards.
