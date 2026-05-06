def test_scoring_endpoint_works(client):
    response = client.post(
        "/api/v1/scoring/anomaly",
        json={
            "source": "api",
            "event_type": "error_rate",
            "signal_type": "error_rate",
            "entity_id": "service-api",
            "payload": {"value": 55},
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert set(body.keys()) >= {
        "z_score",
        "isolation_score",
        "rolling_score",
        "seasonal_score",
        "detector_scores",
        "selected_detector",
        "combined_score",
        "dynamic_threshold",
        "confidence_score",
        "severity",
        "reason_codes",
        "is_anomalous",
        "explanation",
    }
    assert body["selected_detector"] in {"error_rate", "default"}


def test_scoring_explanation_contains_deviation_and_direction(client):
    low = client.post(
        "/api/v1/scoring/anomaly",
        json={
            "source": "api",
            "event_type": "cpu_usage",
            "signal_type": "cpu_usage",
            "entity_id": "node-1",
            "payload": {"value": 30},
        },
    )
    assert low.status_code == 200

    high = client.post(
        "/api/v1/scoring/anomaly",
        json={
            "source": "api",
            "event_type": "cpu_usage",
            "signal_type": "cpu_usage",
            "entity_id": "node-1",
            "payload": {"value": 95},
        },
    )
    assert high.status_code == 200
    body = high.json()
    assert any(level == body["severity"] for level in ["low", "medium", "high"])
    assert "deviation=" in body["explanation"]
    assert "direction=spike" in body["explanation"] or "direction=drop" in body["explanation"]
