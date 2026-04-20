# Pulse AI MVP Architecture

- **Backend**: FastAPI + SQLAlchemy for ingestion, scoring, alerting, and aggregate metrics.
- **ML scoring**: blended Z-score and Isolation Forest score persisted per event.
- **Storage**: PostgreSQL tables: `events`, `anomaly_scores`, `alerts`.
- **Frontend**: React + Vite + Tailwind dashboard with Recharts visualizations and source filters.
- **Runtime**: docker-compose orchestrates Postgres, backend API, and frontend UI.
