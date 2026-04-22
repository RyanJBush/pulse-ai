def _ingest(client, value: float, entity_id: str = "entity-ai-1"):
    return client.post(
        "/api/v1/events/ingest",
        json={
            "source": "checkout",
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": entity_id,
            "payload": {"value": value},
        },
    )


def test_ai_anomaly_summary_and_daily_briefing(client):
    for value in [10.0, 9.8, 10.2, 9.9, 10.1, 9.7, 10.0, 10.2, 10.3, 9.9, 10.1, 10.0, 280.0]:
        _ingest(client, value)

    latest_scores = client.get("/api/v1/events", params={"limit": 1})
    assert latest_scores.status_code == 200

    alerts = client.get("/api/v1/alerts")
    assert alerts.status_code == 200
    assert alerts.json()

    # score id can be inferred from first alert anomaly_score_id
    anomaly_score_id = alerts.json()[0]["anomaly_score_id"]
    summary = client.get(
        f"/api/v1/ai/anomalies/{anomaly_score_id}/summary",
        headers={"x-role": "analyst"},
    )
    assert summary.status_code == 200
    body = summary.json()
    assert body["anomaly_score_id"] == anomaly_score_id
    assert body["suggested_next_steps"]

    briefing = client.get("/api/v1/ai/daily-briefing", headers={"x-role": "viewer"})
    assert briefing.status_code == 200
    briefing_body = briefing.json()
    assert set(briefing_body.keys()) >= {
        "day",
        "total_events",
        "anomalies",
        "alerts",
        "top_entities",
        "repeated_patterns",
        "briefing",
    }


def test_ai_incident_wrap_up(client):
    for value in [10.0] * 15 + [300.0]:
        _ingest(client, value, entity_id="entity-ai-2")

    incidents = client.get("/api/v1/incidents", headers={"x-role": "operator"})
    assert incidents.status_code == 200
    incident_id = incidents.json()[0]["id"]

    note = client.post(
        f"/api/v1/incidents/{incident_id}/notes",
        headers={"x-role": "operator"},
        json={"author": "op-1", "note": "Captured timeline."},
    )
    assert note.status_code == 201

    wrap = client.get(
        f"/api/v1/ai/incidents/{incident_id}/wrap-up",
        headers={"x-role": "analyst"},
    )
    assert wrap.status_code == 200
    wrap_body = wrap.json()
    assert wrap_body["incident_id"] == incident_id
    assert wrap_body["timeline_points"]
    assert wrap_body["recommended_followups"]
