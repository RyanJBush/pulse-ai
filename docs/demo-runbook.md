# Orbit — Demo Runbook

A scripted 5–7 minute walkthrough for recruiter / interview screen-shares. Every command
below works against a fresh `docker compose up` of this repo — no external services, no
secrets. The "incidents" are synthetic streams replayed deterministically against the
local stack.

> A shorter "what to look at" version lives at the top of [`README.md`](../README.md#-recruiter-demo-in-2-minutes).
> Use this runbook when you're driving a live demo and need an exact sequence.

---

## 0. Pre-flight (do this before the call)

```bash
docker compose up --build       # First boot ≈90 s. Subsequent boots ≈10 s.
# In another terminal:
make demo-replay                # Pre-seed a few hundred events so the dashboard isn't empty.
```

Verify three URLs respond:

- `http://localhost:8000/health` → `{"status":"ok"}`
- `http://localhost:8000/docs` → Swagger UI lists 9 routers / 34 endpoints.
- `http://localhost:4173` → operator dashboard renders KPI cards.

Open these tabs in this order so you can flip through them during the demo:

1. Operator dashboard — `http://localhost:4173`
2. Swagger UI — `http://localhost:8000/docs`
3. Terminal with `run_demo.py` ready to invoke
4. `docs/observability.md` open to the latency-spike example

---

## 1. Opening (60 seconds)

Say out loud:

> "Orbit is a real-time anomaly detection and monitoring platform — think a stripped-down
> Datadog. It ingests time-series events, scores them with a blended detector
> (Z-score + Isolation Forest + rolling + a seasonal proxy), and walks alerts through an
> incident lifecycle. It's a portfolio project — not deployed, no real users. Every
> incident in this demo is a synthetic stream I'm replaying."

Show the README's [Project / Technical Snapshot](../README.md#-project--technical-snapshot)
table — call out 34 endpoints, 10 models, 40 tests, CI-gated.

---

## 2. Live KPI dashboard (60 seconds)

Switch to `http://localhost:4173`. Point at:

- **KPI cards** — latency p50/p95, error rate, throughput, anomaly rate, severity mix.
- **Trend chart** — entity drill-down (pick `checkout-svc`); call out that the red points
  are events whose blended confidence crossed the threshold.
- **Alerts table** — filter to severity `high`/`critical`.

Say: *"Everything you see is wired to live REST endpoints — there's no static fixture."*

---

## 3. Inject a latency spike (90 seconds)

In your terminal:

```bash
python backend/scripts/run_demo.py --count 200 --seed 77 --spike-every 10
```

Explain while it runs:

- Same `--seed` → same event stream → reproducible threshold tuning.
- `--spike-every 10` injects an out-of-distribution value every 10th event.
- Each event goes through `ScoringService`: four detectors, weighted blend, a single
  0–1 confidence score.
- When the blended score crosses `ANOMALY_THRESHOLD` (default 0.75) **and** the source
  isn't in a cooldown window (`ALERT_COOLDOWN_SECONDS=300`), an alert is created.

Refresh the dashboard. New alerts should appear; the trend chart should show the spikes.

---

## 4. Open the lifecycle (90 seconds)

In the dashboard:

1. Click the top-severity alert → review the rationale (detector breakdown, threshold,
   reason codes).
2. `PATCH` the alert: **Open → Acknowledged**, add a note ("Investigating — looks like
   the upstream cache thrashed.").
3. Group the alert into an incident; add an incident note.
4. Resolve.

Switch to Swagger UI and open `GET /api/v1/governance/audit-logs` — show the audit log
entries that just got written. Say: *"Every state transition writes to an append-only
audit log. That's the difference between a noisy alert firehose and a tool an operator
would actually keep open."*

---

## 5. Evaluation tooling (90 seconds)

This is the differentiator — most portfolio anomaly projects skip it.

In Swagger UI (or via `curl`):

```bash
# Step 1 — seeded benchmark
curl -X POST http://localhost:8000/api/v1/evaluation/seeded-benchmark \
  -H 'content-type: application/json' \
  -H 'x-role: analyst' \
  -d '{"count": 300, "seed": 42, "inject_spike_every": 12}'

# Step 2 — sweep thresholds against the same seeded run
curl -X POST http://localhost:8000/api/v1/evaluation/threshold-tuning \
  -H 'content-type: application/json' \
  -H 'x-role: analyst' \
  -d '{"thresholds": [0.6, 0.7, 0.75, 0.8, 0.85, 0.9]}'
```

Say:

> "Threshold tuning emits precision / recall / FPR per threshold and recommends one. So
> when I change the detection threshold, I can show — not assert — that recall held up
> and the false-positive rate didn't blow out."

---

## 6. Architecture wrap (45 seconds)

Switch to `README.md` and scroll to the Mermaid architecture diagram. Trace the path:

> "Event hits `/api/v1/events/ingest` → `EventService` writes the row → `ScoringService`
> blends four detectors → `AlertService` checks cooldown / suppression → an `Alert` and
> an `audit_log` row land in Postgres → the React + Recharts UI polls the metrics
> endpoint and re-renders."

Then open the [Limitations table](../README.md#-limitations--future-work) and call out
two things explicitly:

- **Throughput-floor alerts are planned, not implemented** — the KPI shows a drop, but
  the platform doesn't auto-emit on it yet.
- **Seasonal baseline is a minute-bucket proxy** — full Fourier/STL decomposition is on
  the roadmap.

Saying "this is the seam I'd push next" beats handwaving.

---

## 7. Close (30 seconds)

> "End-to-end: data model → ingest → blended scoring → alert lifecycle → incident
> grouping → audit log → operator dashboard, plus the evaluation tooling that makes
> detector changes safe. Forty pytest tests gate every push via GitHub Actions, and the
> whole stack boots with `docker compose up --build`. If you have 15 minutes, the next
> thing I'd show is the threshold-tuning loop on a different signal type."

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Dashboard is empty | Run `make demo-replay` to seed events. |
| `/docs` is blank | Backend hasn't started — check `docker compose logs backend`. |
| `403 insufficient role` on evaluation/governance | Add `-H 'x-role: analyst'` (or `operator`/`admin`) to the curl call. |
| `429 rate limit exceeded` | You exceeded `RATE_LIMIT_PER_MINUTE=240`. Wait a minute or bump the env var. |
| Port 4173 already in use | Stop the conflicting process or change the host port mapping in `docker-compose.yml`. |
| Postgres won't start | `docker compose down -v` to wipe the `pg_data` volume, then `up` again. |

---

## Recording the demo

If you want a Loom / asciinema instead of a live screen-share:

- Resolution: 1440×900 or 1920×1080 — both fit Loom's defaults.
- Hide the OS dock and silence notifications.
- Use the runbook above verbatim; aim for 5–7 minutes.
- After recording, drop links into the README's [Screenshots / Demo](../README.md#-screenshots--demo) section.
