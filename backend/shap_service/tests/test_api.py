from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200


def test_risk_score():

    payload = {
        "usage_decline": 0.55,
        "tickets_last30": 3,
        "negative_sentiment": 0.72,
        "feature_dropout": 0.60,
        "active_days": 2,
        "support_delay": 14,
        "payment_delay": 3
    }

    response = client.post("/risk/score", json=payload)

    assert response.status_code == 200