# Resume Bullets — Orbit (Real-Time Anomaly Detection and Monitoring Platform)

Use these for SRE/observability-oriented applications while preserving accurate portfolio scope.

## Core bullets (accuracy-first)

- Built **Orbit**, a local full-stack anomaly detection and monitoring portfolio demo with FastAPI, PostgreSQL, and React, demonstrating event ingest → scoring → alert triage → incident workflow.
- Implemented blended anomaly scoring (Z-score, Isolation Forest, rolling baseline, minute-bucket seasonal proxy) to produce confidence-based anomaly decisions.
- Shipped REST APIs for events, scoring, alerts, incidents, metrics, evaluation, and governance, with OpenAPI docs for recruiter/interviewer walkthroughs.
- Implemented alert lifecycle state transitions and analyst notes, plus incident status tracking to model SRE-style triage workflows.
- Added detector evaluation/tuning endpoints to compare thresholds and detector behavior on deterministic seeded replay runs.

## Scope disclaimer line (recommended under project entry)

- Portfolio scope: local Docker demo with synthetic replay traffic; no production deployment, no Kafka-class streaming bus, no external paging integration, and no enterprise auth stack.

## Optional variants

- Built a dashboard that demonstrates KPI monitoring, anomaly trend analysis, alerts triage, and incident workflow state management.
- Designed APIs and data models that separate implemented capabilities from planned roadmap items to avoid overclaiming production readiness.
