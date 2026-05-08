def test_event_buffer_enqueue_flush_and_stats(client):
    enqueue = client.post(
        "/api/v1/events/buffer/enqueue",
        json={
            "events": [
                {
                    "workspace_id": "ws-buffer",
                    "source": "buffer-source",
                    "event_type": "latency",
                    "signal_type": "latency",
                    "entity_id": "node-1",
                    "payload": {"value": 10.0},
                },
                {
                    "workspace_id": "ws-buffer",
                    "source": "buffer-source",
                    "event_type": "latency",
                    "signal_type": "latency",
                    "entity_id": "node-1",
                    "payload": {"value": 280.0},
                },
            ]
        },
    )
    assert enqueue.status_code == 202
    assert enqueue.json()["accepted"] == 2

    stats_before = client.get("/api/v1/events/buffer/stats")
    assert stats_before.status_code == 200
    assert stats_before.json()["queued"] >= 2

    flush = client.post("/api/v1/events/buffer/flush", params={"limit": 2})
    assert flush.status_code == 200
    assert flush.json()["processed"] == 2

    stats_after = client.get("/api/v1/events/buffer/stats")
    assert stats_after.status_code == 200
    assert stats_after.json()["total_flushed"] >= 2

    events = client.get("/api/v1/events", params={"workspace_id": "ws-buffer"})
    assert events.status_code == 200
    assert len(events.json()) >= 2


def test_monitoring_simulation_start_and_anomaly_injection(client):
    start = client.post(
        "/api/v1/events/simulation/start",
        json={
            "workspace_id": "ws-sim",
            "source": "monitoring-sim",
            "entity_id": "entity-sim-1",
            "steps": 4,
            "interval_seconds": 1,
            "inject_spike_every": 2,
            "seed": 99,
        },
    )
    assert start.status_code == 200
    start_body = start.json()
    assert start_body["ingested_events"] == 12
    assert start_body["run_id"]

    inject = client.post(
        "/api/v1/events/simulation/inject-anomaly",
        json={
            "workspace_id": "ws-sim",
            "source": "monitoring-sim",
            "entity_id": "entity-sim-1",
            "metric": "request_volume",
            "magnitude": 5.0,
        },
    )
    assert inject.status_code == 201
    inject_body = inject.json()
    assert inject_body["event"]["signal_type"] == "request_volume"
    assert "explanation" in inject_body
