"""End-to-end tests: POST via TestClient → GET via TestClient, verify round-trip through real DB."""
from datetime import datetime, timezone


def test_diaper_roundtrip(client):
    post = client.post("/api/v1/changes/", json={
        "adult_id": 1,
        "change_type_id": 1,
        "accident": True,
    })
    assert post.status_code == 201
    assert post.json()["status"] == "success"

    get = client.get("/api/v1/changes/?limit=10")
    assert get.status_code == 200
    rows = get.json()
    assert len(rows) == 1
    assert rows[0]["change_type"] == "pee"
    assert rows[0]["accident"] is True
    assert rows[0]["change_time"] is not None


def test_sleep_roundtrip_with_duration(client):
    start = "2026-04-17T10:00:00+00:00"
    end = "2026-04-17T11:30:00+00:00"
    post = client.post("/api/v1/sleep/", json={
        "adult_id": 2,
        "started_at": start,
        "ended_at": end,
        "notes": "middag",
    })
    assert post.status_code == 201

    get = client.get("/api/v1/sleep/?hours=168")
    assert get.status_code == 200
    rows = get.json()
    assert len(rows) == 1
    assert rows[0]["duration_minutes"] == 90
    assert rows[0]["notes"] == "middag"


def test_sleep_ongoing_has_no_end(client):
    post = client.post("/api/v1/sleep/", json={"adult_id": 1})
    assert post.status_code == 201

    rows = client.get("/api/v1/sleep/?hours=24").json()
    assert len(rows) == 1
    assert rows[0]["ended_at"] is None
    assert rows[0]["duration_minutes"] is None


def test_food_bottle_roundtrip(client):
    post = client.post("/api/v1/food/", json={
        "adult_id": 1,
        "food_type": "bottle",
        "amount_ml": 120,
    })
    assert post.status_code == 201

    rows = client.get("/api/v1/food/?hours=24").json()
    assert len(rows) == 1
    assert rows[0]["food_type"] == "bottle"
    assert rows[0]["amount_ml"] == 120


def test_food_breast_no_amount(client):
    post = client.post("/api/v1/food/", json={
        "adult_id": 2,
        "food_type": "breast",
    })
    assert post.status_code == 201

    rows = client.get("/api/v1/food/?hours=24").json()
    assert rows[0]["food_type"] == "breast"
    assert rows[0]["amount_ml"] is None


def test_invalid_food_type_rejected_at_db_layer(client):
    # Pydantic rejects before hitting DB
    res = client.post("/api/v1/food/", json={"adult_id": 1, "food_type": "fizzy"})
    assert res.status_code == 422


def test_fk_violation_returns_400(client):
    # adult_id=999 doesn't exist, FK should fail
    res = client.post("/api/v1/changes/", json={
        "adult_id": 999,
        "change_type_id": 1,
    })
    assert res.status_code == 400
