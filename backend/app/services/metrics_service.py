from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.cache import TTLCache
from app.core.config import settings
from app.models.alert import Alert
from app.models.anomaly_score import AnomalyScore
from app.models.event import Event
from app.schemas.metrics import EntityDrilldownMetrics, KpiSummary


class MetricsService:
    _summary_cache: TTLCache[KpiSummary] = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)

    def __init__(self, db: Session):
        self.db = db

    def kpi_summary(self) -> KpiSummary:
        cached = self._summary_cache.get("kpi_summary")
        if cached is not None:
            return cached
        total_scores = self.db.scalar(select(func.count(AnomalyScore.id))) or 0
        anomalous_scores = (
            self.db.scalar(
                select(func.count(AnomalyScore.id)).where(AnomalyScore.is_anomalous.is_(True))
            )
            or 0
        )
        alert_count = self.db.scalar(select(func.count(Alert.id))) or 0
        high_severity = (
            self.db.scalar(
                select(func.count(AnomalyScore.id)).where(
                    AnomalyScore.severity.in_(("high", "critical")),
                )
            )
            or 0
        )
        avg_latency = self.db.scalar(select(func.avg(AnomalyScore.scoring_latency_ms))) or 0.0

        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=5)
        recent_events = (
            self.db.scalar(select(func.count(Event.id)).where(Event.created_at >= cutoff)) or 0
        )
        throughput_per_minute = round(float(recent_events) / 5.0, 4)

        anomaly_rate = (
            0.0
            if total_scores == 0
            else round(float(anomalous_scores) / float(total_scores), 4)
        )
        summary = KpiSummary(
            anomaly_rate=anomaly_rate,
            alert_count=alert_count,
            throughput_per_minute=throughput_per_minute,
            high_severity_anomalies=high_severity,
            avg_scoring_latency_ms=round(float(avg_latency), 4),
        )
        self._summary_cache.set("kpi_summary", summary)
        return summary

    def entity_drilldown(self, entity_id: str) -> EntityDrilldownMetrics:
        total_events = (
            self.db.scalar(select(func.count(Event.id)).where(Event.entity_id == entity_id))
            or 0
        )
        anomalous_events = (
            self.db.scalar(
                select(func.count(AnomalyScore.id))
                .join(Event, Event.id == AnomalyScore.event_id)
                .where(Event.entity_id == entity_id)
                .where(AnomalyScore.is_anomalous.is_(True))
            )
            or 0
        )
        active_alerts = (
            self.db.scalar(
                select(func.count(Alert.id))
                .join(Event, Event.id == Alert.event_id)
                .where(Event.entity_id == entity_id)
                .where(Alert.status.in_(("new", "acknowledged", "investigating")))
            )
            or 0
        )
        avg_score = (
            self.db.scalar(
                select(func.avg(AnomalyScore.combined_score))
                .join(Event, Event.id == AnomalyScore.event_id)
                .where(Event.entity_id == entity_id)
            )
            or 0.0
        )
        last_event_at = self.db.scalar(
            select(func.max(Event.event_timestamp)).where(Event.entity_id == entity_id)
        )

        severity_rows = self.db.execute(
            select(AnomalyScore.severity, func.count(AnomalyScore.id))
            .join(Event, Event.id == AnomalyScore.event_id)
            .where(Event.entity_id == entity_id)
            .group_by(AnomalyScore.severity)
        ).all()
        severity_distribution = {row[0]: int(row[1]) for row in severity_rows}

        reason_rows = self.db.execute(
            select(AnomalyScore.reason_codes)
            .join(Event, Event.id == AnomalyScore.event_id)
            .where(Event.entity_id == entity_id)
        ).all()
        reason_code_distribution: dict[str, int] = {}
        for row in reason_rows:
            for code in row[0] or []:
                reason_code_distribution[code] = reason_code_distribution.get(code, 0) + 1

        anomaly_rate = (
            0.0
            if total_events == 0
            else round(float(anomalous_events) / float(total_events), 4)
        )
        return EntityDrilldownMetrics(
            entity_id=entity_id,
            total_events=total_events,
            anomalous_events=anomalous_events,
            anomaly_rate=anomaly_rate,
            active_alerts=active_alerts,
            avg_combined_score=round(float(avg_score), 4),
            last_event_at=last_event_at,
            severity_distribution=severity_distribution,
            reason_code_distribution=reason_code_distribution,
        )
