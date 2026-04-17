"""Verify that hours=N filters correctly exclude older rows."""
from app.db import get_connection


def _insert_old_sleep(hours_ago: int, adult_id: int = 1):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO sleep_sessions (baby_id, adult_id, started_at)
               VALUES (?, ?, DATE_SUB(UTC_TIMESTAMP(), INTERVAL ? HOUR))""",
            (1, adult_id, hours_ago),
        )
        conn.commit()


def _insert_old_food(hours_ago: int, adult_id: int = 1):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO food_intake (baby_id, adult_id, food_type, logged_at)
               VALUES (?, ?, 'bottle', DATE_SUB(UTC_TIMESTAMP(), INTERVAL ? HOUR))""",
            (1, adult_id, hours_ago),
        )
        conn.commit()


def test_sleep_24h_excludes_older(client):
    _insert_old_sleep(hours_ago=2)
    _insert_old_sleep(hours_ago=30)

    rows_24 = client.get("/api/v1/sleep/?hours=24").json()
    rows_48 = client.get("/api/v1/sleep/?hours=48").json()
    rows_72 = client.get("/api/v1/sleep/?hours=72").json()

    assert len(rows_24) == 1
    assert len(rows_48) == 2
    assert len(rows_72) == 2


def test_food_1week_filter(client):
    _insert_old_food(hours_ago=1)
    _insert_old_food(hours_ago=100)
    _insert_old_food(hours_ago=200)

    rows_24 = client.get("/api/v1/food/?hours=24").json()
    rows_168 = client.get("/api/v1/food/?hours=168").json()
    rows_300 = client.get("/api/v1/food/?hours=300").json()

    assert len(rows_24) == 1
    assert len(rows_168) == 2
    assert len(rows_300) == 3


def test_order_descending(client):
    _insert_old_food(hours_ago=5)
    _insert_old_food(hours_ago=1)
    _insert_old_food(hours_ago=10)

    rows = client.get("/api/v1/food/?hours=24").json()
    times = [r["logged_at"] for r in rows]
    assert times == sorted(times, reverse=True)
