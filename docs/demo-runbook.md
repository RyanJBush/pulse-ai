# Orbit — Demo Runbook (Local Portfolio Walkthrough)

Goal: clearly show what Orbit demonstrates today without overstating production readiness.

## Setup

```bash
docker compose up --build
make demo-replay
```

Open:
- `http://localhost:4173` (dashboard)
- `http://localhost:8000/docs` (API docs)

## Demo script (5 minutes)

1. **Set context (30s).**
   - "Orbit is a local SRE/observability portfolio demo using synthetic replayed events."

2. **Dashboard (60s).**
   - Show KPI cards as operational snapshot.
   - Clarify this is local polling UI, not production NOC tooling.

3. **Anomaly trend chart (60s).**
   - Choose an entity and show trend + anomaly score behavior during replay spikes.
   - Mention current seasonality is a minute-bucket proxy.

4. **Alerts table (60s).**
   - Show open/acknowledged/resolved workflow and notes.
   - Clarify no external notifier integration (Slack/PagerDuty/email) yet.

5. **Incident workflow (60s).**
   - Show alert grouping, incident status changes, and notes.
   - Call out auditability intent (state transitions tracked in persistence).

6. **API + boundaries (30s).**
   - Show `/docs` route groups.
   - State auth is `X-Role` role gating only (portfolio scope).

## Optional command during demo

```bash
python backend/scripts/run_demo.py --count 200 --seed 77 --spike-every 10
```

Use this to generate fresh anomalies while the UI is visible.
