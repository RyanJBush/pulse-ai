# Orbit Screenshot Documentation

These screenshots support the README narrative for **Orbit — Real-Time Anomaly Detection and Monitoring Platform** as a local portfolio demo.

## What each screenshot demonstrates

1. `01-kpi-dashboard.png`
   - Demonstrates the dashboard-level operational snapshot in the local UI.
2. `02-anomaly-trend-chart.png`
   - Demonstrates trend behavior and anomaly signal movement for a selected entity.
3. `03-alerts-table.png`
   - Demonstrates alert queue triage and status-oriented analyst workflow.
4. `04-incident-drawer.png`
   - Demonstrates incident handling workflow (state + notes context).
5. `05-api-docs.png`
   - Demonstrates breadth of API surface via local Swagger docs.

## Accuracy notes to keep with screenshots

- Images represent a **local Docker demo** driven by synthetic replay events.
- They do not imply production deployment, enterprise auth, or external paging integrations.
- UI reflects REST-polling behavior (not guaranteed streaming push architecture).
- Seasonal behavior visuals should be described as proxy baseline behavior unless full seasonal decomposition is implemented.

## Capture refresh commands

```bash
docker compose up --build
make demo-replay
python backend/scripts/run_demo.py --count 200 --seed 77 --spike-every 10
```
