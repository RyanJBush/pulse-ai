![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![CI](https://github.com/RyanJBush/Real-time-anomaly-detection-and-monitoring-platform/actions/workflows/ci.yml/badge.svg)

# Pulse AI

> A production-style anomaly detection and monitoring platform that ingests real-time events, scores them with a blended ML pipeline, generates alerts, and exposes a live operator dashboard — built to mirror how observability tools like Datadog and New Relic work under the hood.

---

## 🎯 What I Built & Why

Observability platforms are everywhere in production engineering, but the internals — how an event stream becomes an alert, how anomaly thresholds are tuned, how incidents are tracked — are rarely taught. I built Pulse AI to work through that entire lifecycle end-to-end:

- **Blended scoring** — Z-score + Isolation Forest + rolling/seasonal baselines, combined into a single confidence score. No single algorithm catches all anomaly shapes; combining them reduces both false positives and missed events.
- **Replay & evaluation tooling** — detector configuration is only as good as its evaluation. The replay engine lets you test threshold changes against historical event windows before deploying them.
- **Incident workflow** — alerts alone aren't enough. Pulse AI groups alerts into incidents and provides a notes/status lifecycle so analysts can track investigation state without leaving the platform.

---

## 📷 Features

- **Real-time event ingestion** — stream, simulate, and batch-replay security/metric events
- **Multi-detector scoring** — Z-score, Isolation Forest, rolling mean, and seasonal baselines blended into a confidence score
- **Alert & incident management** — auto-generated alerts with status workflow, analyst notes, and incident grouping
- **Evaluation tooling** — seeded benchmark runs, threshold tuning, and detector comparison endpoints
- **Live operator dashboard** — React + Recharts UI with entity trend views and KPI cards
- **Docker Compose** — one-command local stack with Postgres, backend, and frontend

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + SQLAlchemy + PostgreSQL |
| ML / Detection | scikit-learn (Isolation Forest), pandas (Z-score, rolling) |
| Frontend | React + Vite + Tailwind CSS + Recharts |
| Infra | Docker Compose + GitHub Actions CI |
| Linting / Testing | ruff + pytest |

---

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.11+
- Node.js 20+

### Docker (Recommended)
```bash
docker compose up --build
# Backend API docs: http://localhost:8000/docs
# Frontend:         http://localhost:5173
# PostgreSQL:        localhost:5432
```

### Local Development
```bash
# Backend
pip install -e ./backend[dev]
uvicorn app.main:app --app-dir backend --reload

# Frontend
npm --prefix frontend install
npm --prefix frontend run dev
```

Set `VITE_API_BASE_URL` if the backend is not running on `http://localhost:8000`.

### Demo — Replay & Simulation
```bash
# Run synthetic replay demo (prints replay metadata + anomalous events)
make demo-replay

# Or with custom parameters
python backend/scripts/run_demo.py --count 200 --seed 77 --spike-every 10
```

For the interactive UI demo:
1. Open the dashboard at `http://localhost:5173`
2. Click **Start monitoring simulation** to begin periodic CPU/API latency/request volume updates
3. Click **Inject anomaly** to force a high-confidence anomaly event for live alert demo

### Quality Checks
```bash
make lint
make test
make build
```

---

## 🗂️ Repository Structure

```
backend/    FastAPI API, SQLAlchemy models, anomaly scoring, evaluation logic, pytest + ruff
frontend/   React + Vite operator dashboard
docs/       Architecture, API reference, deployment guide, demo walkthrough
```

---

## 📝 Key Learnings

- Blended detectors (Z-score + Isolation Forest) meaningfully outperform single-algorithm approaches, especially on irregular metric shapes
- Replay/evaluation tooling is as important as the detector itself — you can't responsibly tune thresholds without a way to test them against historical data
- Incident management (grouping + lifecycle) is the difference between a monitoring tool and a useful operations product

---

## 📄 Additional Docs

- API reference: `docs/api.md`
- Architecture overview: `docs/architecture.md`
- Deployment guide: `docs/deployment.md`
- Demo walkthrough: `docs/demo.md`
- Repository guide: `docs/repository-guide.md`

---

## 📄 License

MIT
