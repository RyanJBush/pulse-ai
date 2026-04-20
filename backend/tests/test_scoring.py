def test_scoring_endpoint_works(client):
    response = client.post(
        "/api/v1/scoring/anomaly",
        json={"source": "api", "event_type": "error_rate", "payload": {"value": 55}},
    )
    assert response.status_code == 200

    body = response.json()
    assert set(body.keys()) == {
        "z_score",
        "isolation_score",
        "combined_score",
        "is_anomalous",
        "explanation",
    }
