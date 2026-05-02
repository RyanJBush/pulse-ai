def _ingest(client, value: float, entity_id: str = "entity-coverage", *, source: str = "svc"):
    return client.post(
        "/api/v1/events/ingest",
        json={
            "source": source,
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": entity_id,
            "payload": {"value": value},
        },
    )


def test_governance_detector_upsert_validation_and_audit_log(client):
    bad = client.put(
        "/api/v1/governance/detectors",
        headers={"x-role": "admin"},
        json={
            "signal_type": "latency",
            "z_weight": 0,
            "isolation_weight": 0,
            "rolling_weight": 0,
            "seasonal_weight": 0,
            "enabled": True,
            "actor": "admin-1",
        },
    )
    assert bad.status_code == 400
    assert "greater than 0" in bad.json()["detail"]

    upsert = client.put(
        "/api/v1/governance/detectors",
        headers={"x-role": "admin"},
        json={
            "signal_type": " Latency ",
            "z_weight": 0.4,
            "isolation_weight": 0.3,
            "rolling_weight": 0.2,
            "seasonal_weight": 0.1,
            "enabled": True,
            "actor": "admin-1",
        },
    )
    assert upsert.status_code == 200
    assert upsert.json()["signal_type"] == "latency"

    logs = client.get("/api/v1/governance/audit-logs?limit=5", headers={"x-role": "admin"})
    assert logs.status_code == 200
    assert any(row["action"] == "detector_config_upsert" for row in logs.json())


def test_incident_update_rejects_invalid_status_and_missing_incident(client):
    invalid = client.patch(
        "/api/v1/incidents/999",
        headers={"x-role": "operator"},
        json={"status": "madeup", "actor": "op-1"},
    )
    assert invalid.status_code == 400
    assert "invalid incident status" in invalid.json()["detail"]

    missing = client.patch(
        "/api/v1/incidents/999",
        headers={"x-role": "operator"},
        json={"status": "investigating", "actor": "op-1"},
    )
    assert missing.status_code == 404
    assert missing.json()["detail"] == "incident not found"


def test_threshold_tuning_and_detector_comparison_endpoints(client):
    baseline = [10.0, 10.2, 9.8, 10.1, 10.0, 9.9, 10.3, 10.1, 10.0, 9.8, 10.2, 10.1]
    for value in baseline:
        _ingest(client, value, entity_id="entity-eval", source="eval")
    _ingest(client, 300.0, entity_id="entity-eval", source="eval")

    tuning = client.post(
        "/api/v1/evaluation/threshold-tuning",
        headers={"x-role": "analyst"},
        json={
            "workspace_id": "default",
            "source": "eval",
            "signal_type": "latency",
            "entity_id": "entity-eval",
            "thresholds": [0.6, 0.7, 0.8, 0.9],
        },
    )
    assert tuning.status_code == 200
    body = tuning.json()
    assert len(body["points"]) == 4
    assert body["recommended_threshold"] in {0.6, 0.7, 0.8, 0.9}

    comparison = client.post(
        "/api/v1/evaluation/detector-comparison",
        headers={"x-role": "analyst"},
        json={
            "workspace_id": "default",
            "source": "eval",
            "signal_type": "latency",
            "entity_id": "entity-eval",
        },
    )
    assert comparison.status_code == 200
    detectors = comparison.json()["detectors"]
    assert len(detectors) >= 1
    assert all("detector" in row and "samples" in row for row in detectors)


def test_rate_limit_resets_after_minute_rollover(client, monkeypatch):
    import app.main as main_module

    main_module._rate_limiter.clear()
    monkeypatch.setattr(main_module.settings, "RATE_LIMIT_PER_MINUTE", 1)

    first = client.get("/health")
    second = client.get("/health")
    assert first.status_code == 200
    assert second.status_code == 429

    old_count, old_minute = main_module._rate_limiter["testclient"]
    main_module._rate_limiter["testclient"] = (old_count, old_minute - 1)
    reset = client.get("/health")
    assert reset.status_code == 200
