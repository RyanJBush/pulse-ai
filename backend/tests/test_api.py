from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_event_ingestion_and_listing():
    created = client.post(
        "/api/events",
        json={"source_id": "sensor-a", "event_type": "temperature", "value": 21.5, "payload": {}},
    )

    assert created.status_code == 200
    assert created.json()["source_id"] == "sensor-a"

    listed = client.get("/api/events")
    assert listed.status_code == 200
    assert len(listed.json()) >= 1


def test_scoring_alerts_and_metrics():
    for idx in range(12):
        client.post(
            "/api/events",
            json={
                "source_id": "sensor-b",
                "event_type": "latency",
                "value": 10 + (idx % 2),
                "payload": {"window": idx},
            },
        )

    anomaly_event = client.post(
        "/api/events",
        json={"source_id": "sensor-b", "event_type": "latency", "value": 98.0, "payload": {}},
    ).json()

    score = client.post(
        "/api/anomaly/score",
        json={"event_id": anomaly_event["id"], "threshold": 0.3},
    )

    assert score.status_code == 200
    body = score.json()
    assert body["combined_score"] >= 0.3
    assert body["alert_id"] is not None

    latest = client.get(f"/api/anomaly/{anomaly_event['id']}")
    assert latest.status_code == 200

    alerts = client.get("/api/alerts")
    assert alerts.status_code == 200
    assert len(alerts.json()) >= 1

    metrics = client.get("/api/metrics/summary")
    assert metrics.status_code == 200
    assert metrics.json()["total_events"] >= 13
