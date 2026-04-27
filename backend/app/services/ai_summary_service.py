from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.cache import TTLCache
from app.core.config import settings
from app.models.alert import Alert
from app.models.anomaly_score import AnomalyScore
from app.models.event import Event
from app.models.incident import Incident
from app.models.incident_note import IncidentNote
from app.schemas.ai import AnomalySummaryRead, DailyBriefingRead, IncidentWrapUpRead


class AISummaryService:
    _briefing_cache: TTLCache[DailyBriefingRead] = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)

    def __init__(self, db: Session):
        self.db = db

    def anomaly_summary(self, anomaly_score_id: int) -> AnomalySummaryRead:
        score = self.db.get(AnomalyScore, anomaly_score_id)
        if score is None:
            raise HTTPException(status_code=404, detail="anomaly score not found")

        event = self.db.get(Event, score.event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="event not found for anomaly score")

        primary_reason = score.reason_codes[0] if score.reason_codes else "NO_STRONG_SIGNAL"
        summary = (
            f"{score.severity.upper()} anomaly on {event.signal_type} "
            f"for entity {event.entity_id}. "
            f"Combined score {score.combined_score:.3f} exceeded threshold "
            f"{score.dynamic_threshold:.3f}."
        )
        explanation = (
            f"Signal source={event.source}, value={event.value:.3f}. "
            f"Reason codes={','.join(score.reason_codes)}; primary={primary_reason}; "
            f"confidence={score.confidence_score:.3f}."
        )

        actions = [
            "Validate the metric at source and compare with neighboring entities.",
            "Check upstream deploys or infrastructure changes in the same timeframe.",
            "If persistent for >15 minutes, escalate to incident commander.",
        ]
        if score.severity == "critical":
            actions.insert(0, "Page on-call immediately and start incident bridge.")

        return AnomalySummaryRead(
            anomaly_score_id=anomaly_score_id,
            summary=summary,
            explanation=explanation,
            suggested_next_steps=actions,
        )

    def daily_briefing(self, day: date | None = None) -> DailyBriefingRead:
        use_day = day or datetime.now(timezone.utc).date()
        cache_key = f"daily:{use_day.isoformat()}"
        cached = self._briefing_cache.get(cache_key)
        if cached is not None:
            return cached
        start = datetime.combine(use_day, time.min)
        end = start + timedelta(days=1)

        total_events = (
            self.db.scalar(
                select(func.count(Event.id))
                .where(Event.created_at >= start)
                .where(Event.created_at < end)
            )
            or 0
        )
        anomalies = (
            self.db.scalar(
                select(func.count(AnomalyScore.id))
                .where(AnomalyScore.created_at >= start)
                .where(AnomalyScore.created_at < end)
                .where(AnomalyScore.is_anomalous.is_(True))
            )
            or 0
        )
        alerts = (
            self.db.scalar(
                select(func.count(Alert.id))
                .where(Alert.created_at >= start)
                .where(Alert.created_at < end)
            )
            or 0
        )
        high_severity_alerts = (
            self.db.scalar(
                select(func.count(Alert.id))
                .where(Alert.created_at >= start)
                .where(Alert.created_at < end)
                .where(Alert.severity.in_(("high", "critical")))
            )
            or 0
        )

        entity_rows = self.db.execute(
            select(Event.entity_id, func.count(Event.id).label("cnt"))
            .where(Event.created_at >= start)
            .where(Event.created_at < end)
            .group_by(Event.entity_id)
            .order_by(func.count(Event.id).desc())
            .limit(5)
        ).all()
        top_entities = [{"entity_id": row[0], "count": int(row[1])} for row in entity_rows]

        pattern_rows = self.db.execute(
            select(AnomalyScore.reason_codes)
            .where(AnomalyScore.created_at >= start)
            .where(AnomalyScore.created_at < end)
        ).all()
        pattern_counts: dict[str, int] = {}
        for row in pattern_rows:
            key = "+".join(sorted((row[0] or ["NO_STRONG_SIGNAL"])[:2]))
            pattern_counts[key] = pattern_counts.get(key, 0) + 1

        repeated_patterns = [
            {"pattern": key, "count": count}
            for key, count in sorted(
                pattern_counts.items(), key=lambda item: item[1], reverse=True
            )[:5]
        ]

        top_noisy_entity = top_entities[0]["entity_id"] if top_entities else "n/a"
        briefing = (
            f"Daily briefing for {use_day.isoformat()}: {anomalies} anomalies "
            f"from {total_events} events, {alerts} alerts generated "
            f"({high_severity_alerts} high/critical). "
            f"Top noisy entity: {top_noisy_entity}."
        )

        response = DailyBriefingRead(
            day=use_day,
            total_events=int(total_events),
            anomalies=int(anomalies),
            alerts=int(alerts),
            high_severity_alerts=int(high_severity_alerts),
            top_entities=top_entities,
            repeated_patterns=repeated_patterns,
            briefing=briefing,
        )
        self._briefing_cache.set(cache_key, response)
        return response

    def incident_wrap_up(self, incident_id: int) -> IncidentWrapUpRead:
        incident = self.db.get(Incident, incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="incident not found")

        alerts = self.db.scalars(
            select(Alert).where(Alert.incident_id == incident_id).order_by(Alert.created_at.asc())
        ).all()
        notes = self.db.scalars(
            select(IncidentNote)
            .where(IncidentNote.incident_id == incident_id)
            .order_by(IncidentNote.created_at.asc())
        ).all()

        timeline_points = [
            f"{incident.created_at.isoformat()} incident opened with severity={incident.severity}",
            f"{len(alerts)} linked alerts, "
            f"{incident.suppressed_alerts_count} suppressed duplicates",
        ]
        timeline_points.extend(
            [f"{note.created_at.isoformat()} {note.author}: {note.note}" for note in notes[:5]]
        )

        wrap_up = (
            f"Incident {incident_id} ({incident.group_key}) is {incident.status}. "
            f"Owner={incident.assigned_owner or 'unassigned'}. "
            f"Evidence keys={','.join(sorted((incident.evidence or {}).keys())) or 'none'}."
        )

        followups = [
            "Document root cause and add detector tuning recommendations.",
            "Create regression monitor for this incident pattern.",
            "Review suppression/cooldown settings to reduce duplicate noise.",
        ]

        return IncidentWrapUpRead(
            incident_id=incident_id,
            wrap_up=wrap_up,
            timeline_points=timeline_points,
            recommended_followups=followups,
        )
