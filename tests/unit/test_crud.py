from datetime import datetime, timezone, timedelta

import mariadb
import pytest

from app import crud
from app.schemas import DiaperChangeCreate, SleepCreate, FoodCreate


class TestHelpers:
    def test_as_utc_none(self):
        assert crud._as_utc(None) is None

    def test_as_utc_naive_gets_utc_tz(self):
        dt = datetime(2026, 4, 17, 12, 0)
        result = crud._as_utc(dt)
        assert result.tzinfo is timezone.utc

    def test_as_utc_aware_unchanged(self):
        dt = datetime(2026, 4, 17, 12, 0, tzinfo=timezone.utc)
        assert crud._as_utc(dt) is dt

    def test_to_naive_utc_none(self):
        assert crud._to_naive_utc(None) is None

    def test_to_naive_utc_naive_returned_asis(self):
        dt = datetime(2026, 4, 17, 12, 0)
        assert crud._to_naive_utc(dt) is dt

    def test_to_naive_utc_aware_converted(self):
        cet = timezone(timedelta(hours=2))
        dt = datetime(2026, 4, 17, 14, 30, tzinfo=cet)
        result = crud._to_naive_utc(dt)
        assert result.tzinfo is None
        assert result == datetime(2026, 4, 17, 12, 30)


class TestCreateDiaperChange:
    def test_success(self, fake_db):
        fake_db.configure(lastrowid=42)
        change = DiaperChangeCreate(adult_id=1, change_type_id=2, accident=True)
        result = crud.create_diaper_change(change)
        assert result == {"status": "success", "id": 42}
        fake_db.cursor.execute.assert_called_once()
        sql, args = fake_db.cursor.execute.call_args[0]
        assert "INSERT INTO diaper_changes" in sql
        assert args == (1, 2, True, 1)
        fake_db.conn.commit.assert_called_once()

    def test_db_error(self, fake_db):
        fake_db.configure(execute_raises=mariadb.Error("boom"))
        change = DiaperChangeCreate(adult_id=1, change_type_id=1)
        result = crud.create_diaper_change(change)
        assert result["status"] == "error"
        assert "boom" in result["message"]


class TestGetRecentChanges:
    def test_returns_utc_aware_times(self, fake_db):
        naive_dt = datetime(2026, 4, 17, 12, 0)
        fake_db.configure(rows=[("Papa", "pee", 0, naive_dt)])
        result = crud.get_recent_changes(limit=5)
        assert len(result) == 1
        assert result[0]["adult"] == "Papa"
        assert result[0]["change_type"] == "pee"
        assert result[0]["accident"] is False
        assert result[0]["change_time"].tzinfo is timezone.utc

    def test_passes_limit_to_sql(self, fake_db):
        fake_db.configure(rows=[])
        crud.get_recent_changes(limit=25)
        _, args = fake_db.cursor.execute.call_args[0]
        assert args == (25,)

    def test_empty_result(self, fake_db):
        fake_db.configure(rows=[])
        assert crud.get_recent_changes() == []


class TestCreateSleepSession:
    def test_success_with_aware_dt(self, fake_db):
        fake_db.configure(lastrowid=7)
        cet = timezone(timedelta(hours=2))
        sleep = SleepCreate(
            adult_id=2,
            started_at=datetime(2026, 4, 17, 14, 30, tzinfo=cet),
            ended_at=datetime(2026, 4, 17, 16, 30, tzinfo=cet),
            notes="slept fine",
        )
        result = crud.create_sleep_session(sleep)
        assert result == {"status": "success", "id": 7}
        _, args = fake_db.cursor.execute.call_args[0]
        # started/ended converted to naive UTC (CEST -2h)
        assert args[2] == datetime(2026, 4, 17, 12, 30)
        assert args[3] == datetime(2026, 4, 17, 14, 30)
        assert args[4] == "slept fine"

    def test_none_started_at_passes_through(self, fake_db):
        fake_db.configure()
        sleep = SleepCreate(adult_id=1)
        crud.create_sleep_session(sleep)
        _, args = fake_db.cursor.execute.call_args[0]
        assert args[2] is None  # COALESCE handles it in SQL

    def test_db_error(self, fake_db):
        fake_db.configure(execute_raises=mariadb.Error("fail"))
        result = crud.create_sleep_session(SleepCreate(adult_id=1))
        assert result["status"] == "error"


class TestGetSleepSessions:
    def test_duration_calculation(self, fake_db):
        start = datetime(2026, 4, 17, 10, 0)
        end = datetime(2026, 4, 17, 11, 30)
        fake_db.configure(rows=[("Papa", start, end, "nap")])
        result = crud.get_sleep_sessions(hours=24)
        assert result[0]["duration_minutes"] == 90
        assert result[0]["started_at"].tzinfo is timezone.utc
        assert result[0]["ended_at"].tzinfo is timezone.utc

    def test_ongoing_sleep_no_duration(self, fake_db):
        fake_db.configure(rows=[("Mama", datetime(2026, 4, 17, 10, 0), None, None)])
        result = crud.get_sleep_sessions()
        assert result[0]["duration_minutes"] is None
        assert result[0]["ended_at"] is None

    def test_passes_hours_to_sql(self, fake_db):
        fake_db.configure(rows=[])
        crud.get_sleep_sessions(hours=168)
        _, args = fake_db.cursor.execute.call_args[0]
        assert args == (168,)


class TestCreateFoodIntake:
    def test_success(self, fake_db):
        fake_db.configure(lastrowid=3)
        food = FoodCreate(adult_id=1, food_type="bottle", amount_ml=120, notes="good")
        result = crud.create_food_intake(food)
        assert result == {"status": "success", "id": 3}
        _, args = fake_db.cursor.execute.call_args[0]
        assert args == (1, 1, "bottle", 120, "good")

    def test_breast_without_amount(self, fake_db):
        fake_db.configure()
        crud.create_food_intake(FoodCreate(adult_id=1, food_type="breast"))
        _, args = fake_db.cursor.execute.call_args[0]
        assert args[3] is None

    def test_db_error(self, fake_db):
        fake_db.configure(execute_raises=mariadb.Error("oops"))
        result = crud.create_food_intake(FoodCreate(adult_id=1, food_type="solid"))
        assert result["status"] == "error"


class TestGetFoodIntake:
    def test_returns_utc_aware(self, fake_db):
        logged = datetime(2026, 4, 17, 9, 0)
        fake_db.configure(rows=[("Papa", "bottle", 150, logged, None)])
        result = crud.get_food_intake(hours=48)
        assert len(result) == 1
        assert result[0]["amount_ml"] == 150
        assert result[0]["logged_at"].tzinfo is timezone.utc

    def test_default_hours(self, fake_db):
        fake_db.configure(rows=[])
        crud.get_food_intake()
        _, args = fake_db.cursor.execute.call_args[0]
        assert args == (24,)
