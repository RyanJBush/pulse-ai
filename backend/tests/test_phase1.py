def test_serving_predict_default_model(client):
    response = client.post("/api/v1/serving/predict", json={"features": [1.0, 2.0, 3.0]})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["model_name"] == "weighted_sum"
    assert body["prediction"] == 2.333333


def test_serving_predict_validation_and_unknown_model(client):
    invalid = client.post("/api/v1/serving/predict", json={"features": []})
    assert invalid.status_code == 422

    unknown = client.post(
        "/api/v1/serving/predict",
        json={"features": [10.0], "model_name": "missing_model"},
    )
    assert unknown.status_code == 400
    assert "unknown model" in unknown.json()["detail"]

    not_finite = client.post("/api/v1/predict", json={"features": [1.0, "NaN"]})
    assert not_finite.status_code == 422


def test_serving_health(client):
    response = client.get("/api/v1/serving/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["active_model"] == "weighted_sum"
    assert set(body["active_models"]) == {"mean_baseline", "weighted_sum"}


def test_predict_alias_endpoint(client):
    response = client.post("/api/v1/predict", json={"features": [2.0, 4.0]})
    assert response.status_code == 200
    assert response.json()["model_name"] == "weighted_sum"
