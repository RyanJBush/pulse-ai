# Orbit Screenshot Guide

## Captured screenshots currently in the repository

- [x] `docs/screenshots/01-kpi-dashboard.png` — KPI overview dashboard
- [x] `docs/screenshots/02-anomaly-trend-chart.png` — anomaly trend visualization
- [x] `docs/screenshots/03-alerts-table.png` — alert triage table
- [x] `docs/screenshots/04-incident-drawer.png` — incident workflow drawer
- [x] `docs/screenshots/05-api-docs.png` — Swagger / API docs view

## Accuracy notes

- These images reflect a **local portfolio demo** run.
- Data shown is generated from seeded synthetic replay flows.
- UI updates are polling-based in the current implementation.
- Seasonal behavior shown should be described as minute-bucket proxy behavior.
- External Slack, PagerDuty, and email alerting are planned, not implemented.

## If recapturing screenshots

```bash
docker compose up --build
make demo-replay
python backend/scripts/run_demo.py --count 200 --seed 77 --spike-every 10
```
