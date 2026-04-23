def test_governance_detector_config_and_audit_logs(client):
    update = client.put(
        "/api/v1/governance/detectors",
        headers={"x-role": "admin"},
        json={
            "signal_type": "latency",
            "z_weight": 0.25,
            "isolation_weight": 0.4,
            "rolling_weight": 0.25,
            "seasonal_weight": 0.1,
            "enabled": True,
            "actor": "admin-user",
        },
    )
    assert update.status_code == 200
    assert update.json()["signal_type"] == "latency"

    configs = client.get("/api/v1/governance/detectors", headers={"x-role": "analyst"})
    assert configs.status_code == 200
    assert len(configs.json()) == 1

    audit = client.get("/api/v1/governance/audit-logs", headers={"x-role": "operator"})
    assert audit.status_code == 200
    assert audit.json()[0]["action"] == "detector_config_upsert"


def test_evaluation_seeded_benchmark(client):
    response = client.post(
        "/api/v1/evaluation/seeded-benchmark",
        headers={"x-role": "analyst"},
        json={
            "benchmark_name": "phase2-seeded",
            "replay": {
                "seed": 17,
                "count": 35,
                "source": "eval-demo",
                "event_type": "latency",
                "signal_type": "latency",
                "entity_id": "entity-eval-1",
                "inject_spike_every": 7,
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["benchmark_name"] == "phase2-seeded"
    assert body["total_events"] == 35
    assert set(body.keys()) >= {
        "precision",
        "recall",
        "false_positive_rate",
        "mean_alert_latency_seconds",
        "time_to_first_detect_seconds",
        "detector_breakdown",
    }


def test_rbac_blocks_low_privilege_for_governance(client):
    denied = client.put(
        "/api/v1/governance/detectors",
        headers={"x-role": "viewer"},
        json={
            "signal_type": "cpu",
            "z_weight": 0.3,
            "isolation_weight": 0.3,
            "rolling_weight": 0.3,
            "seasonal_weight": 0.1,
            "enabled": False,
            "actor": "viewer",
        },
    )
    assert denied.status_code == 403


def test_governance_detector_config_rejects_non_positive_total_weight(client):
    response = client.put(
        "/api/v1/governance/detectors",
        headers={"x-role": "admin"},
        json={
            "signal_type": "latency",
            "z_weight": 0.0,
            "isolation_weight": 0.0,
            "rolling_weight": 0.0,
            "seasonal_weight": 0.0,
            "enabled": True,
            "actor": "admin-user",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "detector weights must sum to greater than 0"
