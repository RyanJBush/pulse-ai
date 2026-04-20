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
