from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app import schemas


class TestDiaperChangeCreate:
    def test_valid(self):
        m = schemas.DiaperChangeCreate(adult_id=1, change_type_id=2)
        assert m.adult_id == 1
        assert m.change_type_id == 2
        assert m.accident is False
        assert m.baby_id == 1

    def test_accident_flag(self):
        m = schemas.DiaperChangeCreate(adult_id=1, change_type_id=1, accident=True)
        assert m.accident is True

    @pytest.mark.parametrize("adult_id", [0, -1])
    def test_adult_id_must_be_positive(self, adult_id):
        with pytest.raises(ValidationError):
            schemas.DiaperChangeCreate(adult_id=adult_id, change_type_id=1)

    def test_change_type_id_must_be_positive(self):
        with pytest.raises(ValidationError):
            schemas.DiaperChangeCreate(adult_id=1, change_type_id=0)

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            schemas.DiaperChangeCreate(adult_id=1)


class TestDiaperChangeRead:
    def test_serializes_aware_datetime_with_tz(self):
        dt = datetime(2026, 4, 17, 12, 30, tzinfo=timezone.utc)
        m = schemas.DiaperChangeRead(adult="Papa", change_type="pee", change_time=dt)
        payload = m.model_dump_json()
        assert "+00:00" in payload or "Z" in payload

    def test_change_time_optional(self):
        m = schemas.DiaperChangeRead(adult="Papa", change_type="pee")
        assert m.change_time is None


class TestSleepCreate:
    def test_all_defaults(self):
        m = schemas.SleepCreate(adult_id=1)
        assert m.started_at is None
        assert m.ended_at is None
        assert m.notes is None
        assert m.baby_id == 1

    def test_accepts_naive_datetime(self):
        m = schemas.SleepCreate(adult_id=1, started_at=datetime(2026, 4, 17, 10, 0))
        assert m.started_at.tzinfo is None

    def test_accepts_aware_datetime_string(self):
        m = schemas.SleepCreate(adult_id=1, started_at="2026-04-17T10:00:00+02:00")
        assert m.started_at.tzinfo is not None

    def test_adult_id_must_be_positive(self):
        with pytest.raises(ValidationError):
            schemas.SleepCreate(adult_id=0)


class TestSleepRead:
    def test_duration_optional(self):
        m = schemas.SleepRead(adult="Papa", started_at=datetime(2026, 4, 17, 10, 0))
        assert m.duration_minutes is None
        assert m.ended_at is None


class TestFoodCreate:
    @pytest.mark.parametrize("food_type", ["breast", "bottle", "solid"])
    def test_valid_food_types(self, food_type):
        m = schemas.FoodCreate(adult_id=1, food_type=food_type)
        assert m.food_type == food_type

    @pytest.mark.parametrize("food_type", ["fizzy", "", "BREAST", "formula"])
    def test_invalid_food_type_rejected(self, food_type):
        with pytest.raises(ValidationError):
            schemas.FoodCreate(adult_id=1, food_type=food_type)

    def test_amount_must_be_positive(self):
        with pytest.raises(ValidationError):
            schemas.FoodCreate(adult_id=1, food_type="bottle", amount_ml=0)

    def test_amount_optional(self):
        m = schemas.FoodCreate(adult_id=1, food_type="breast")
        assert m.amount_ml is None


class TestFoodRead:
    def test_basic(self):
        m = schemas.FoodRead(
            adult="Papa",
            food_type="bottle",
            amount_ml=120,
            logged_at=datetime(2026, 4, 17, 10, 0, tzinfo=timezone.utc),
        )
        payload = m.model_dump_json()
        assert '"amount_ml":120' in payload


class TestAdult:
    def test_basic(self):
        m = schemas.Adult(adult_id=1, name="Papa")
        assert m.adult_id == 1
        assert m.name == "Papa"
