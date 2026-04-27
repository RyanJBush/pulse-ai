# Demo Walkthrough

This walkthrough is intended for recruiter/interview demos (~5–10 minutes).

## 1) Startup

```bash
docker compose up --build
```

Open UI at `http://localhost:4173`.

## 2) Generate data

From another terminal:

```bash
make demo-replay
```

Or use UI replay controls in the Dashboard/Events views.

## 3) Show real-time monitoring

- KPI cards update (anomaly rate, throughput, high-severity anomalies).
- Buffer health cards (queued/enqueued/flushed).
- Alert timeline and severity distribution.

## 4) Drill down

- Use Entity drill-down selector to inspect per-entity anomaly rates.
- Show anomaly rationale table (detector, combined score, threshold, reason codes).

## 5) Workflow UX

- Alerts page:
  - select an alert,
  - transition lifecycle status,
  - add investigation note.
- Incident panel:
  - update incident status,
  - add incident note.

## 6) Detector evaluation (Phase 4)

Open Metrics page “Detector evaluation lab”:

- run seeded benchmark,
- tune thresholds and explain recommended threshold,
- compare detector TPR/FPR.

## 7) Close

Emphasize:

- end-to-end flow from event ingest to scoring to alert/incident actions,
- evaluation tooling for model governance,
- dockerized local run and CI checks.
