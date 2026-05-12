# Observability & Incident-Style Examples

Orbit is a portfolio project — these examples describe how the platform behaves against
**simulated** event streams. There are no real users, real on-call rotations, or live
production traffic behind these scenarios. They exist to show how an event would flow
through ingest → score → alert → incident in a real observability tool.

---

## System metrics tracked

| Metric | Surfaced by | Source field on `Event` |
|---|---|---|
| Latency (p50 / p95 of recent values) | `GET /api/v1/metrics/summary`, `GET /api/v1/metrics/entities/{id}` | `value` when `signal_type=latency` |
| Error rate | metrics summary KPI cards | `signal_type=error_rate` |
| Throughput (events / minute) | metrics summary KPI cards | derived from event timestamps |
| Anomaly rate | metrics summary KPI cards | ratio of anomalous scores to total |
| Severity mix (low / medium / high / critical) | metrics summary | derived from `AnomalyScore.severity` |

The frontend renders these as KPI cards plus per-entity trend charts (Recharts line charts).

## Health & readiness

- `GET /health` — liveness probe; always returns 200 if the process is up.
- `GET /ready` — readiness probe; returns 200 once the DB session can be acquired.

These match the standard Kubernetes liveness/readiness contract, even though Orbit is not
deployed to a cluster — they exist so the patterns are correct.

## Logging

Structured request/response logs are emitted by `app.core.logging`. Log level is controlled
by `LOG_LEVEL` (see `.env.example`). Logs include the request path, status code, and
duration so they could be shipped to any standard log aggregator.

---

## Incident-style examples

Each example walks one synthetic scenario from raw event to incident. To replay them
locally, see `docs/demo.md` and `backend/scripts/run_demo.py`.

### 1. Latency spike on a checkout-style entity

**Signal:** `signal_type=latency` for `entity_id=checkout-svc` jumps from a ~120 ms baseline
to ~900 ms over 5 consecutive events.

**What Orbit does:**
1. Each spike event is scored by Z-score (large), Isolation Forest (outlier), and rolling
   mean baseline (large delta). The blended confidence rises above 0.85.
2. `AnomalyScore.severity` is set to `high`. An `Alert` is generated for the entity.
3. The cooldown window (default 300 s) suppresses duplicate alerts on the same entity so
   the operator dashboard does not flood.
4. Subsequent high-severity alerts on the same entity within the window are attached to a
   single `Incident` row with status `open`. Analyst can append notes via
   `POST /api/v1/alerts/{id}/notes`.

**Replay command:**
```bash
python backend/scripts/run_demo.py --signal-type latency --entity-id checkout-svc \
  --count 200 --seed 13 --spike-every 8
```

### 2. Error-rate regression

**Signal:** `signal_type=error_rate` drifts from ~0.5% to ~7% over a 10-minute window.

**What Orbit does:**
1. The rolling mean baseline detects the sustained drift before the Z-score detector does
   (Z-score reacts more to sharp spikes than gradual drift).
2. Confidence climbs steadily; once it crosses `ANOMALY_THRESHOLD` (default 0.75), an alert
   fires with severity `medium`.
3. The seasonal baseline is consulted to check whether this is a recurring weekly pattern;
   if not, the score is not dampened.
4. The incident is grouped under the same entity until the rate falls below threshold.

### 3. Throughput drop (silent failure)

**Signal:** Event throughput for a source drops to zero while no error events are emitted —
a classic "silent failure" that pure error-rate alerting would miss.

**What Orbit does:**
1. The metrics service tracks events-per-minute per source.
2. A throughput-floor check (planned/future — see Limitations) would emit a synthetic
   `low_throughput` event into the pipeline.
3. That synthetic event is scored and alerted on like any other.

> **Planned:** the throughput-floor producer is not yet implemented; today the drop is
> visible on the dashboard KPI card but does not auto-emit an alert. This is the next
> meaningful feature to add and is called out in the README's Limitations section.

---

## Tuning the detector

- `ANOMALY_THRESHOLD` controls the confidence floor for emitting an alert.
- `ALERT_COOLDOWN_SECONDS` controls per-entity suppression after a fired alert.
- Use `POST /api/v1/evaluation/threshold-tuning` to sweep thresholds against a seeded
  benchmark and get a recommended value with precision/recall/FPR per threshold.
- Use `POST /api/v1/evaluation/detector-comparison` to compare individual detector TPR/FPR
  on the same replay window — useful for deciding whether to keep Isolation Forest in the
  blend for a given signal shape.

---

## What this is not

- Not a deployed production system.
- Not connected to real telemetry sources (no OpenTelemetry collector, no Prometheus scrape).
- Not paging anyone — alerts live in the database and dashboard only.
- Not load-tested at scale.

These limits are intentional and called out so reviewers can calibrate expectations.
