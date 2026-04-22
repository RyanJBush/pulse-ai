def _ingest(client, value: float, workspace_id: str, entity_id: str = "svc-a"):
    return client.post(
        "/api/v1/events/ingest",
        json={
            "workspace_id": workspace_id,
            "source": "checkout",
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": entity_id,
            "payload": {"value": value},
        },
    )


def test_workspace_filtering_for_events_and_alerts(client):
    for value in [10.0, 10.1, 9.9, 10.2, 10.0, 9.8, 10.1, 10.0, 9.9, 10.2, 10.1, 10.0, 280.0]:
        _ingest(client, value, workspace_id="ws-a", entity_id="node-1")
    for value in [8.0, 8.1, 8.2, 8.1, 8.0]:
        _ingest(client, value, workspace_id="ws-b", entity_id="node-2")

    ws_a_events = client.get("/api/v1/events", params={"workspace_id": "ws-a"})
    ws_b_events = client.get("/api/v1/events", params={"workspace_id": "ws-b"})
    assert ws_a_events.status_code == 200
    assert ws_b_events.status_code == 200
    assert all(item["workspace_id"] == "ws-a" for item in ws_a_events.json())
    assert all(item["workspace_id"] == "ws-b" for item in ws_b_events.json())

    ws_a_alerts = client.get("/api/v1/alerts", params={"workspace_id": "ws-a"})
    assert ws_a_alerts.status_code == 200
    assert ws_a_alerts.json()
    assert all(item["workspace_id"] == "ws-a" for item in ws_a_alerts.json())


def test_suppression_rules_block_alerts_in_workspace(client):
    rule = client.post(
        "/api/v1/governance/suppression-rules",
        headers={"x-role": "admin"},
        json={
            "workspace_id": "ws-suppress",
            "entity_id": "svc-1",
            "signal_type": "latency",
            "reason": "known maintenance",
            "actor": "admin-user",
        },
    )
    assert rule.status_code == 201

    for value in [10.0] * 12 + [300.0]:
        _ingest(client, value, workspace_id="ws-suppress", entity_id="svc-1")

    alerts = client.get("/api/v1/alerts", params={"workspace_id": "ws-suppress"})
    assert alerts.status_code == 200
    assert alerts.json() == []

    listed = client.get(
        "/api/v1/governance/suppression-rules",
        headers={"x-role": "analyst"},
        params={"workspace_id": "ws-suppress"},
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["workspace_id"] == "ws-suppress"
