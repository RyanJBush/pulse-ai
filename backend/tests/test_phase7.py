def _ingest(client, value: float, workspace: str = "ws-eval", entity: str = "svc-eval"):
    return client.post(
        "/api/v1/events/ingest",
        json={
            "workspace_id": workspace,
            "source": "benchmark",
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": entity,
            "payload": {"value": value},
        },
    )


def test_threshold_tuning_and_detector_comparison(client):
    replay = client.post(
        "/api/v1/events/replay",
        json={
            "workspace_id": "ws-eval",
            "source": "benchmark",
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": "svc-eval",
            "seed": 123,
            "count": 40,
            "inject_spike_every": 8,
        },
    )
    assert replay.status_code == 201

    tuning = client.post(
        "/api/v1/evaluation/threshold-tuning",
        headers={"x-role": "analyst"},
        json={
            "workspace_id": "ws-eval",
            "source": "benchmark",
            "signal_type": "latency",
            "entity_id": "svc-eval",
            "thresholds": [0.6, 0.7, 0.8, 0.9],
        },
    )
    assert tuning.status_code == 200
    tuning_body = tuning.json()
    assert tuning_body["recommended_threshold"] is not None
    assert len(tuning_body["points"]) == 4

    compare = client.post(
        "/api/v1/evaluation/detector-comparison",
        headers={"x-role": "analyst"},
        json={
            "workspace_id": "ws-eval",
            "source": "benchmark",
            "signal_type": "latency",
            "entity_id": "svc-eval",
        },
    )
    assert compare.status_code == 200
    compare_body = compare.json()
    assert compare_body["detectors"]
    assert set(compare_body["detectors"][0].keys()) >= {
        "detector",
        "samples",
        "true_positive_rate",
        "false_positive_rate",
    }
