def _ingest(client, value: float, entity_id: str = "entity-ops-1"):
    return client.post(
        "/api/v1/events/ingest",
        json={
            "source": "payments",
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": entity_id,
            "payload": {"value": value},
        },
    )


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_alert_lifecycle_and_notes(client):
    for value in [10.1, 10.0, 9.9, 10.2, 10.1, 9.8, 10.0, 10.2, 10.1, 9.9, 10.3, 10.0]:
        _ingest(client, value)
    anomaly = _ingest(client, 280.0).json()
    assert anomaly["is_anomalous"] is True

    alert_id = anomaly["alert_id"]
    assert alert_id is not None

    updated = client.patch(
        f"/api/v1/alerts/{alert_id}/status",
        json={"status": "acknowledged", "author": "operator-1", "note": "Investigating spike"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "acknowledged"

    note = client.post(
        f"/api/v1/alerts/{alert_id}/notes",
        json={"author": "operator-1", "note": "Checked upstream latency."},
    )
    assert note.status_code == 201

    notes = client.get(f"/api/v1/alerts/{alert_id}/notes")
    assert notes.status_code == 200
    assert len(notes.json()) >= 2


def test_metrics_summary_and_entity_drilldown(client):
    for value in [18.0, 18.5, 19.0, 18.7, 45.0, 18.6]:
        _ingest(client, value, entity_id="entity-metrics-1")

    summary = client.get("/api/v1/metrics/summary")
    assert summary.status_code == 200
    summary_body = summary.json()
    assert set(summary_body.keys()) == {
        "anomaly_rate",
        "alert_count",
        "throughput_per_minute",
        "high_severity_anomalies",
        "avg_scoring_latency_ms",
    }

    drilldown = client.get("/api/v1/metrics/entities/entity-metrics-1")
    assert drilldown.status_code == 200
    drilldown_body = drilldown.json()
    assert drilldown_body["entity_id"] == "entity-metrics-1"
    assert drilldown_body["total_events"] == 6
    assert "severity_distribution" in drilldown_body
    assert "reason_code_distribution" in drilldown_body
