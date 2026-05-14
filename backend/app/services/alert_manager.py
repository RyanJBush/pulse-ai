from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import redis

from app.core.config import settings


class AlertManager:
    def __init__(self):
        self.cooldown_seconds = settings.ALERT_DEDUP_COOLDOWN_SECONDS
        self._client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def _dedup_key(self, workspace_id: str, entity_id: str, signal_type: str) -> str:
        return f"dedup:{workspace_id}:{entity_id}:{signal_type}"

    def _suppress_key(self, workspace_id: str, metric: str) -> str:
        return f"suppressed:{workspace_id}:{metric}"

    def is_duplicate(self, *, workspace_id: str, entity_id: str, signal_type: str) -> bool:
        return self._client.exists(self._dedup_key(workspace_id, entity_id, signal_type)) == 1

    def mark_fired(self, *, workspace_id: str, entity_id: str, signal_type: str) -> None:
        self._client.setex(
            self._dedup_key(workspace_id, entity_id, signal_type), self.cooldown_seconds, "1"
        )

    def suppress_metric(self, *, workspace_id: str, metric: str, duration_minutes: int) -> dict:
        until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        payload = {"metric": metric, "suppressed_until": until.isoformat()}
        self._client.setex(
            self._suppress_key(workspace_id, metric), duration_minutes * 60, json.dumps(payload)
        )
        return payload

    def is_suppressed(self, *, workspace_id: str, metric: str) -> bool:
        return self._client.exists(self._suppress_key(workspace_id, metric)) == 1
