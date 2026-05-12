# Orbit Screenshot Guide

## Captured screenshots in repository

- [x] `docs/screenshots/01-kpi-dashboard.png` — KPI dashboard snapshot
- [x] `docs/screenshots/02-anomaly-trend-chart.png` — anomaly trend view
- [x] `docs/screenshots/03-alerts-table.png` — alert triage table
- [x] `docs/screenshots/04-incident-drawer.png` — incident detail workflow
- [x] `docs/screenshots/05-api-docs.png` — FastAPI Swagger docs

## Accuracy and claim boundaries

- Captures reflect a local **portfolio-scale anomaly detection demo**.
- Data is seeded synthetic replay data.
- Event flow is replay-simulated, not backed by Kafka/Kinesis/WebSocket streaming infrastructure.
- Alerting screenshots show in-app triage; external Slack/PagerDuty/email notifications are planned.
- Dashboard refresh behavior is polling-based in current implementation.

## Recapture workflow

```bash
make dev-start
```

Then capture the UI/API states listed above.
