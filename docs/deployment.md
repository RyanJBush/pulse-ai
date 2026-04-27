# Deployment Guide

## Option 1: Docker Compose (recommended for demos)

```bash
docker compose up --build
```

Access:

- API: `http://localhost:8000`
- UI: `http://localhost:4173`

## Option 2: Split deploy (API + UI)

### Backend

- Build from `backend/Dockerfile`
- Required environment variable:
  - `DATABASE_URL` (PostgreSQL URL)
- Optional tuning:
  - `ANOMALY_THRESHOLD`
  - `ALERT_COOLDOWN_SECONDS`
  - `CACHE_TTL_SECONDS`
  - `RATE_LIMIT_PER_MINUTE`

### Frontend

- Build from `frontend/Dockerfile`
- Required environment variable:
  - `VITE_API_BASE_URL` (public base URL for backend)

## Production checklist

- [ ] Use managed Postgres with backups.
- [ ] Restrict CORS origins (no wildcard).
- [ ] Replace header-only role model with real auth.
- [ ] Set observability (request logs, error alerts).
- [ ] Configure HTTPS/TLS termination.
- [ ] Run regular replay benchmark jobs and track precision/recall drift.
