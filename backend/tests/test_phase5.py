def _ingest(client, value: float, entity: str = "entity-p5"):
    return client.post(
        "/api/v1/events/ingest",
        json={
            "source": "api",
            "event_type": "latency",
            "signal_type": "latency",
            "entity_id": entity,
            "payload": {"value": value},
        },
    )


def test_events_pagination_and_sorting(client):
    for value in [1.0, 2.0, 3.0, 4.0, 5.0]:
        _ingest(client, value, entity="entity-p5-events")

    asc = client.get("/api/v1/events", params={"limit": 2, "offset": 0, "sort_desc": False})
    assert asc.status_code == 200
    asc_items = asc.json()
    assert len(asc_items) == 2
    assert asc_items[0]["value"] <= asc_items[1]["value"]

    page2 = client.get("/api/v1/events", params={"limit": 2, "offset": 2, "sort_desc": False})
    assert page2.status_code == 200
    assert len(page2.json()) == 2


def test_alert_and_incident_pagination_filters(client):
    baseline = [10.0] * 18
    for value in baseline:
        _ingest(client, value, entity="entity-p5-alerts")

    _ingest(client, 280.0, entity="entity-p5-alerts")
    _ingest(client, 290.0, entity="entity-p5-alerts")

    alerts = client.get(
        "/api/v1/alerts", params={"limit": 1, "offset": 0, "sort_desc": True, "status": "new"}
    )
    assert alerts.status_code == 200
    assert len(alerts.json()) == 1

    incidents = client.get(
        "/api/v1/incidents",
        headers={"x-role": "operator"},
        params={"limit": 10, "offset": 0, "sort_desc": True},
    )
    assert incidents.status_code == 200
    assert incidents.json()
    assert incidents.json()[0]["group_key"] == "entity-p5-alerts:latency"


def test_ai_daily_briefing_cached_endpoint_access(client):
    _ingest(client, 42.0, entity="entity-p5-brief")
    res1 = client.get("/api/v1/ai/daily-briefing", headers={"x-role": "viewer"})
    res2 = client.get("/api/v1/ai/daily-briefing", headers={"x-role": "viewer"})
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.json()["day"] == res2.json()["day"]
