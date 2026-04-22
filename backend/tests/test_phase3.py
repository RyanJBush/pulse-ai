def _ingest_latency(client, value: float, entity: str = "entity-inc-1"):
    return client.post(
        "/api/v1/events/ingest",
        json={
            "source": "checkout",
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": entity,
            "payload": {"value": value},
        },
    )


def test_incident_created_from_alert_and_note_workflow(client):
    baseline = [9.8, 10.1, 9.9, 10.2, 10.0, 9.7, 10.1, 9.8, 10.3, 10.0, 9.9, 10.2]
    for value in baseline:
        _ingest_latency(client, value)

    anomaly = _ingest_latency(client, 290.0)
    assert anomaly.status_code == 201
    alert_id = anomaly.json()["alert_id"]
    assert alert_id is not None

    alerts = client.get("/api/v1/alerts")
    assert alerts.status_code == 200
    incident_id = alerts.json()[0]["incident_id"]
    assert incident_id is not None

    incidents = client.get("/api/v1/incidents", headers={"x-role": "analyst"})
    assert incidents.status_code == 200
    assert incidents.json()[0]["id"] == incident_id

    update = client.patch(
        f"/api/v1/incidents/{incident_id}",
        headers={"x-role": "operator"},
        json={
            "status": "investigating",
            "actor": "operator-a",
            "assigned_owner": "oncall-user",
            "note": "Investigating p95 latency spike",
        },
    )
    assert update.status_code == 200
    assert update.json()["status"] == "investigating"
    assert update.json()["assigned_owner"] == "oncall-user"

    notes = client.get(
        f"/api/v1/incidents/{incident_id}/notes", headers={"x-role": "analyst"}
    )
    assert notes.status_code == 200
    assert len(notes.json()) == 1


def test_incident_suppression_counter_increments(client):
    for value in [10.0] * 15:
        _ingest_latency(client, value, entity="entity-inc-2")

    first = _ingest_latency(client, 320.0, entity="entity-inc-2")
    second = _ingest_latency(client, 330.0, entity="entity-inc-2")
    assert first.status_code == 201
    assert second.status_code == 201

    incidents = client.get("/api/v1/incidents", headers={"x-role": "operator"})
    assert incidents.status_code == 200
    matched = [i for i in incidents.json() if i["group_key"] == "entity-inc-2:latency"]
    assert matched
    assert matched[0]["suppressed_alerts_count"] >= 1
