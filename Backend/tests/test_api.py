from uuid import uuid4

from fastapi.testclient import TestClient

from housevalue.api import create_app
from housevalue.enrichment import NeighbourhoodSignals


async def no_network_enrichment(*_args, **_kwargs):
    return NeighbourhoodSignals(schools_within_2km=2, hospitals_within_2km=1, transit_stations_within_2km=1, source="test")


def test_signup_and_predict(monkeypatch):
    monkeypatch.setattr("housevalue.api.fetch_neighbourhood_signals", no_network_enrichment)
    email = f"test-{uuid4().hex}@example.com"
    with TestClient(create_app()) as client:
        signup = client.post("/api/auth/signup", json={"name": "Test User", "email": email, "password": "safe-password-123"})
        assert signup.status_code == 201, signup.text
        token = signup.json()["access_token"]
        prediction = client.post("/api/predict", headers={"Authorization": f"Bearer {token}"}, json={"location": "Kalyan", "bhk": 2, "bathrooms": 2, "area": 757, "property_type": "Apartment", "pincode": "421301"})
    assert prediction.status_code == 200, prediction.text
    body = prediction.json()
    assert body["estimated_price"] > 0
    assert body["neighbourhood_signals"]["source"] == "loading"
    enrichment = client.get("/api/enrichment?latitude=19.25&longitude=73.13", headers={"Authorization": f"Bearer {token}"})
    assert enrichment.status_code == 200
    assert enrichment.json()["schools_within_2km"] == 2
