from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_crud(monkeypatch):
    class Calls:
        def __init__(self):
            self.create_diaper = None
            self.get_changes = None
            self.create_sleep = None
            self.get_sleep = None
            self.create_food = None
            self.get_food = None

    calls = Calls()

    def _patch(name, fn):
        monkeypatch.setattr(f"app.routes.crud.{name}", fn)

    calls.patch = _patch
    return calls


def test_read_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "html" in res.headers["content-type"]


class TestChangesRoutes:
    def test_post_success(self, client, mock_crud):
        mock_crud.patch("create_diaper_change", lambda c: {"status": "success", "id": 1})
        res = client.post("/api/v1/changes/", json={"adult_id": 1, "change_type_id": 1})
        assert res.status_code == 201
        assert res.json() == {"status": "success", "id": 1}

    def test_post_crud_error_returns_400(self, client, mock_crud):
        mock_crud.patch("create_diaper_change", lambda c: {"status": "error", "message": "fk fail"})
        res = client.post("/api/v1/changes/", json={"adult_id": 1, "change_type_id": 1})
        assert res.status_code == 400
        assert res.json()["detail"] == "fk fail"

    def test_post_invalid_body_422(self, client):
        res = client.post("/api/v1/changes/", json={"adult_id": 0, "change_type_id": 1})
        assert res.status_code == 422

    def test_post_missing_field_422(self, client):
        res = client.post("/api/v1/changes/", json={"adult_id": 1})
        assert res.status_code == 422

    def test_get_default_limit(self, client, mock_crud):
        captured = {}

        def stub(limit=10):
            captured["limit"] = limit
            return []

        mock_crud.patch("get_recent_changes", stub)
        res = client.get("/api/v1/changes/")
        assert res.status_code == 200
        assert captured["limit"] == 10

    def test_get_custom_limit(self, client, mock_crud):
        captured = {}

        def stub(limit=10):
            captured["limit"] = limit
            return [{"adult": "Papa", "change_type": "pee", "accident": False,
                     "change_time": datetime(2026, 4, 17, 12, 0, tzinfo=timezone.utc)}]

        mock_crud.patch("get_recent_changes", stub)
        res = client.get("/api/v1/changes/?limit=25")
        assert res.status_code == 200
        assert captured["limit"] == 25
        body = res.json()
        assert len(body) == 1
        assert body[0]["adult"] == "Papa"


class TestSleepRoutes:
    def test_post_success(self, client, mock_crud):
        mock_crud.patch("create_sleep_session", lambda s: {"status": "success", "id": 2})
        res = client.post("/api/v1/sleep/", json={"adult_id": 1})
        assert res.status_code == 201

    def test_post_crud_error_400(self, client, mock_crud):
        mock_crud.patch("create_sleep_session", lambda s: {"status": "error", "message": "db down"})
        res = client.post("/api/v1/sleep/", json={"adult_id": 1})
        assert res.status_code == 400

    def test_post_invalid_adult(self, client):
        res = client.post("/api/v1/sleep/", json={"adult_id": 0})
        assert res.status_code == 422

    def test_get_with_hours(self, client, mock_crud):
        captured = {}

        def stub(hours=24):
            captured["hours"] = hours
            return [{"adult": "Mama", "started_at": datetime(2026, 4, 17, 10, 0, tzinfo=timezone.utc),
                     "ended_at": None, "duration_minutes": None, "notes": None}]

        mock_crud.patch("get_sleep_sessions", stub)
        res = client.get("/api/v1/sleep/?hours=72")
        assert res.status_code == 200
        assert captured["hours"] == 72


class TestFoodRoutes:
    def test_post_success(self, client, mock_crud):
        mock_crud.patch("create_food_intake", lambda f: {"status": "success", "id": 9})
        res = client.post("/api/v1/food/", json={"adult_id": 1, "food_type": "bottle", "amount_ml": 120})
        assert res.status_code == 201

    def test_post_invalid_food_type_422(self, client):
        res = client.post("/api/v1/food/", json={"adult_id": 1, "food_type": "fizzy"})
        assert res.status_code == 422

    def test_post_crud_error_400(self, client, mock_crud):
        mock_crud.patch("create_food_intake", lambda f: {"status": "error", "message": "x"})
        res = client.post("/api/v1/food/", json={"adult_id": 1, "food_type": "breast"})
        assert res.status_code == 400

    def test_get_default_hours(self, client, mock_crud):
        captured = {}

        def stub(hours=24):
            captured["hours"] = hours
            return []

        mock_crud.patch("get_food_intake", stub)
        res = client.get("/api/v1/food/")
        assert res.status_code == 200
        assert captured["hours"] == 24
