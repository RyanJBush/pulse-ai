# Screenshots — capture & embedding guide

This folder is the home for portfolio-quality screenshots embedded in the top-level
[`README.md`](../../README.md#-screenshots--demo). The five PNGs listed below have been
captured against the live local stack; the embedding guide further down stays as
reference for re-capture.

## Captured set (committed)

| File | Captured against | Notes |
|---|---|---|
| `01-kpi-dashboard.png` | `http://localhost:4173` (Vite preview) / dev server | Full-page Dashboard view. The app's actual KPI cards are **Anomaly rate, Alerts, Throughput / min, High severity anomalies, Buffer queued / enqueued / flushed** — there is no p50/p95 or severity-mix card today, so the spec row below is aspirational, not implemented. Severity-mix is shown via the "Alerts by severity" bar chart further down the page. |
| `02-anomaly-trend-chart.png` | Dashboard → "Entity drill-down" with `checkout-svc` selected | The Recharts line chart plots raw metric values plus the combined anomaly score as an overlaid line (not red dots/vertical bands as the original spec suggested). The spikes from the seeded replay are clearly visible. |
| `03-alerts-table.png` | Alerts page → "Alert feed" section | Shows 6 alerts across `acknowledged` / `resolved` states, with metric, anomaly score, timestamp, and the detector explanation column. The app does not currently render severity badges or a severity-filter control, so the table-only shape is the actual UI. |
| `04-incident-drawer.png` | Alerts page → "Alert workflow" + "Incident workflow" articles, side by side | Alert #1 selected (3 analyst notes), Incident #6 selected (3 incident notes, status `investigating`). This is the closest equivalent to an "incident drawer" in the shipped UI — there is no slide-out drawer component. |
| `05-api-docs.png` | `http://localhost:8000/docs` (Swagger UI) | All 9 router tag groups expanded so individual endpoints are visible. Schemas section hidden via CSS to keep the shot focused on the API surface. Surfaces 36 endpoints; the README's "34 endpoints" claim reflects the documented router count and may drift from the live OpenAPI total. |

### Repro

The committed shots were captured with Playwright (`chromium`, viewport `1440x900`,
device scale factor `2`), seeded via `python backend/scripts/run_demo.py` across six
`(entity, signal)` permutations, with several alerts transitioned to `acknowledged`
and `resolved` plus analyst/incident notes added via the REST API. PNGs were resized
to a max width of 1600 px and palette-quantized to keep each file under 400 KB.

If you re-capture: bring up `docker compose up --build`, run a wide seed (multiple
entities/signals so the entity drill-down has options), and follow the per-shot tips
below.

## Five shots, in the order the README references them

| # | File name | What to capture | Why |
|---|---|---|---|
| 1 | `01-kpi-dashboard.png` | Top-of-app KPI cards: latency p50/p95, error rate, throughput, anomaly rate, severity mix. | Tells a recruiter "this is a real dashboard, not a wireframe." |
| 2 | `02-anomaly-trend-chart.png` | Entity drill-down Recharts line chart with at least one anomalous point highlighted (red dot / vertical band). | Shows the ML pipeline producing a visible signal. |
| 3 | `03-alerts-table.png` | Alerts list with severity badges, status column, and a non-trivial number of rows (≥5). Use the severity filter so the shot has visible state. | Shows the alert lifecycle UI, not just the data plane. |
| 4 | `04-incident-drawer.png` | One incident selected, with its linked alerts, status timeline, and at least one analyst note. | Demonstrates the difference between an alert firehose and a real operations product. |
| 5 | `05-api-docs.png` | Swagger UI at `http://localhost:8000/docs` showing the 9 router groups expanded enough to see endpoint counts. | Backs up the "34 endpoints" claim with one glance. |

## How to capture each shot

### Pre-flight (do this once)

```bash
docker compose up --build       # boot the full stack
make demo-replay                # seed events so the dashboard isn't empty
python backend/scripts/run_demo.py --count 400 --seed 77 --spike-every 8
```

You want enough data that severity counts are non-zero and the trend chart has shape.

### General capture rules

- **Viewport:** 1440 × 900 (laptop default) or 1920 × 1080 (full HD). Avoid ultrawide
  resolutions — they don't fit GitHub README columns and look stretched on phones.
- **Theme:** match across all shots. If the app has a dark mode, pick one and stay with it.
- **Browser chrome:** crop it out. A screenshot of Chrome's address bar isn't part of the
  product.
- **PII:** there is no real user data, but still scrub anything that looks like a real
  email, IP, or hostname.
- **Cursor:** hide it (most OS screenshot tools do this by default).
- **File format:** PNG, lossless. Resize to a max width of **1600 px** before committing
  so the repo doesn't bloat — `sips`, `magick`, or `pngquant` all work.
- **File size:** aim for **<400 KB** per image. Run `pngquant --quality=80-90` if
  needed.

### Per-shot tips

1. **`01-kpi-dashboard.png`** — Refresh after the seeded replay so KPIs have moved off
   zero. If your severity mix is all `low`, run the replay again with
   `--spike-every 6` so `high` / `critical` appear.
2. **`02-anomaly-trend-chart.png`** — Select an entity with at least one spike
   (`checkout-svc` if you used the default replay). Hover the spike so the tooltip is
   visible — that's what makes the chart feel live.
3. **`03-alerts-table.png`** — Filter to `severity ∈ {high, critical}` and `status = open`
   so the row count looks meaningful. Five-to-ten rows reads better than a single line.
4. **`04-incident-drawer.png`** — Before capturing: open one alert, transition it to
   `acknowledged`, add a one-sentence analyst note, then group it into an incident with a
   one-sentence incident note. The drawer is most compelling when something is *in* it.
5. **`05-api-docs.png`** — Expand the `events`, `alerts`, `incidents`, `evaluation`, and
   `governance` router groups so the endpoint counts (totaling 34) are visible. Collapse
   the schema section at the bottom; it's noise for this shot.

## File naming & layout

```
docs/screenshots/
├── README.md                     # this file
├── 01-kpi-dashboard.png
├── 02-anomaly-trend-chart.png
├── 03-alerts-table.png
├── 04-incident-drawer.png
└── 05-api-docs.png
```

Keep the numeric prefix — the README's Markdown reference order assumes it.

## Embedding in the README

Replace the existing "screenshots not yet captured" callout in `README.md → Screenshots /
Demo` with:

```markdown
### 1 · KPI dashboard
![KPI dashboard](docs/screenshots/01-kpi-dashboard.png)

### 2 · Anomaly trend chart
![Anomaly trend chart](docs/screenshots/02-anomaly-trend-chart.png)

### 3 · Alerts table
![Alerts table](docs/screenshots/03-alerts-table.png)

### 4 · Incident drawer
![Incident drawer](docs/screenshots/04-incident-drawer.png)

### 5 · API docs (Swagger UI)
![Swagger UI](docs/screenshots/05-api-docs.png)
```

Always give every image meaningful alt text — it's both accessibility and SEO.

## Optional: short demo recording

A 60–90-second Loom or asciinema of `python backend/scripts/run_demo.py` running against
the live UI is the single highest-leverage portfolio asset you can add. Use the script in
[`docs/demo-runbook.md`](../demo-runbook.md). Drop the share link directly under the
screenshots section in the README — don't embed a heavy GIF.

## What not to do

- Don't ship blurry shots from a 1080p monitor scaled to 720p — they'll look amateur next
  to the rest of the project.
- Don't include the OS dock, taskbar, or Slack notifications in the frame.
- Don't compress to JPEG — the dashboard text gets fuzzy. PNG only.
- Don't commit a 4 MB file because "GitHub will handle it." Resize first.
- Don't leave placeholder watermarks (Loom, ScreenStudio) on the final shots.
