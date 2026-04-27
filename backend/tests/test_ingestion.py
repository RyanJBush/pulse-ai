def test_event_ingestion_returns_scoring_fields(client):
    payload = {
        "source": "service-A",
        "event_type": "latency",
        "entity_id": "service-A-node-1",
        "signal_type": "latency",
        "payload": {"value": 101.2, "unit": "ms"},
    }

    response = client.post("/api/v1/events/ingest", json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["event"]["source"] == payload["source"]
    assert "z_score" in body
    assert "isolation_score" in body
    assert "combined_score" in body
    assert "dynamic_threshold" in body
    assert "reason_codes" in body
    assert body["event"]["entity_id"] == payload["entity_id"]
    assert body["is_anomalous"] is False


def test_anomalous_event_creates_alert(client):
    # Build baseline around low values.
    for value in [
        9.5,
        9.8,
        10.0,
        10.2,
        10.1,
        9.9,
        10.0,
        10.1,
        9.8,
        10.2,
        9.7,
        10.3,
        10.0,
        10.1,
        9.9,
        10.2,
        10.0,
        9.8,
        10.1,
        9.9,
        10.0,
        10.2,
    ]:
        client.post(
            "/api/v1/events/ingest",
            json={
                "source": "sensor",
                "event_type": "cpu",
                "signal_type": "cpu",
                "entity_id": "sensor-A",
                "payload": {"value": value},
            },
        )

    response = client.post(
        "/api/v1/events/ingest",
        json={
            "source": "sensor",
            "event_type": "cpu",
            "signal_type": "cpu",
            "entity_id": "sensor-A",
            "payload": {"value": 300.0},
        },
    )
    assert response.status_code == 201
    assert response.json()["is_anomalous"] is True

    alerts = client.get("/api/v1/alerts")
    assert alerts.status_code == 200
    assert len(alerts.json()) >= 1


def test_replay_seeded_stream(client):
    response = client.post(
        "/api/v1/events/replay",
        json={
            "seed": 7,
            "count": 30,
            "source": "demo",
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": "entity-replay",
            "inject_spike_every": 10,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["replay_run_id"]
    assert body["duration_ms"] >= 0
    assert "started_at" in body
    assert "finished_at" in body
    assert body["ingested"] == 30
    assert body["anomalous"] >= 1


def test_scored_events_endpoint_returns_score_rationale(client):
    baseline = [9.8, 10.0, 10.1, 9.9, 10.2, 10.0, 10.1, 9.7, 10.2, 9.9, 10.0, 10.1]
    for value in baseline:
        client.post(
            "/api/v1/events/ingest",
            json={
                "source": "sensor",
                "event_type": "latency",
                "signal_type": "latency",
                "entity_id": "sensor-phase2",
                "payload": {"value": value},
            },
        )

    client.post(
        "/api/v1/events/ingest",
        json={
            "source": "sensor",
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": "sensor-phase2",
            "payload": {"value": 320.0},
        },
    )

    response = client.get("/api/v1/events/scored", params={"anomalous_only": True})
    assert response.status_code == 200
    rows = response.json()
    assert rows
    first = rows[0]
    assert "event" in first
    assert "score" in first
    assert first["score"]["is_anomalous"] is True
    assert first["score"]["reason_codes"]
