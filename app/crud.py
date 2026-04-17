from datetime import datetime, timezone
from app.schemas import DiaperChangeCreate, SleepCreate, FoodCreate
from app.db import get_connection
import mariadb


def _as_utc(dt: datetime | None) -> datetime | None:
    """Wrap a naive datetime from MariaDB (stored in UTC) as tz-aware UTC."""
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _to_naive_utc(dt: datetime | None) -> datetime | None:
    """Convert an incoming (possibly aware) datetime to naive UTC for insert."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def create_diaper_change(change: DiaperChangeCreate):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO diaper_changes (baby_id, change_type_id, accident, adult_id)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, (change.baby_id, change.change_type_id, change.accident, change.adult_id))
            conn.commit()
            return {"status": "success", "id": cursor.lastrowid}
        except mariadb.Error as e:
            return {"status": "error", "message": str(e)}


def get_recent_changes(limit: int = 10):
    with get_connection() as conn:
        cursor = conn.cursor()
        sql = """
            SELECT name, change_type, accident, change_time
            FROM diaper_changes
            JOIN adults USING (adult_id)
            JOIN change_types ON diaper_changes.change_type_id = change_types.change_id
            ORDER BY change_time DESC
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
        result = []
        for (adult, change_type, accident, change_time) in cursor:
            result.append({
                "adult": adult,
                "change_type": change_type,
                "accident": bool(accident),
                "change_time": _as_utc(change_time),
            })
        return result


def create_sleep_session(sleep: SleepCreate):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO sleep_sessions (baby_id, adult_id, started_at, ended_at, notes)
                VALUES (?, ?, COALESCE(?, UTC_TIMESTAMP()), ?, ?)
            """
            cursor.execute(sql, (
                sleep.baby_id,
                sleep.adult_id,
                _to_naive_utc(sleep.started_at),
                _to_naive_utc(sleep.ended_at),
                sleep.notes,
            ))
            conn.commit()
            return {"status": "success", "id": cursor.lastrowid}
        except mariadb.Error as e:
            return {"status": "error", "message": str(e)}


def get_sleep_sessions(hours: int = 24):
    with get_connection() as conn:
        cursor = conn.cursor()
        sql = """
            SELECT name, started_at, ended_at, notes
            FROM sleep_sessions
            JOIN adults USING (adult_id)
            WHERE started_at >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL ? HOUR)
            ORDER BY started_at DESC
        """
        cursor.execute(sql, (hours,))
        result = []
        for (adult, started_at, ended_at, notes) in cursor:
            duration = None
            if ended_at and started_at:
                duration = int((ended_at - started_at).total_seconds() // 60)
            result.append({
                "adult": adult,
                "started_at": _as_utc(started_at),
                "ended_at": _as_utc(ended_at),
                "duration_minutes": duration,
                "notes": notes,
            })
        return result


def create_food_intake(food: FoodCreate):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO food_intake (baby_id, adult_id, food_type, amount_ml, notes)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (food.baby_id, food.adult_id, food.food_type, food.amount_ml, food.notes))
            conn.commit()
            return {"status": "success", "id": cursor.lastrowid}
        except mariadb.Error as e:
            return {"status": "error", "message": str(e)}


def get_food_intake(hours: int = 24):
    with get_connection() as conn:
        cursor = conn.cursor()
        sql = """
            SELECT name, food_type, amount_ml, logged_at, notes
            FROM food_intake
            JOIN adults USING (adult_id)
            WHERE logged_at >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL ? HOUR)
            ORDER BY logged_at DESC
        """
        cursor.execute(sql, (hours,))
        result = []
        for (adult, food_type, amount_ml, logged_at, notes) in cursor:
            result.append({
                "adult": adult,
                "food_type": food_type,
                "amount_ml": amount_ml,
                "logged_at": _as_utc(logged_at),
                "notes": notes,
            })
        return result
