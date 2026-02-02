from app.schemas import DiaperChangeCreate
from app.db import get_connection
import mariadb

def create_diaper_change(change: DiaperChangeCreate):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO diaper_changes (baby_id, change_type_id, accident, adult_id)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, (
                change.baby_id,
                change.change_type_id,
                change.accident,
                change.adult_id
            ))

            conn.commit()
            return {"status": "success", "id": cursor.lastrowid}

        except mariadb.Error as e:
            return {"status": "error", "message": str(e)}


def get_recent_changes(limit: int = 10):
    with get_connection() as conn:

        cursor = conn.cursor()

        sql = """
            SELECT name, change_type, accident
            FROM diaper_changes
            JOIN adults USING (adult_id)
            JOIN change_types ON diaper_changes.change_type_id = change_types.change_id
            ORDER BY change_time DESC
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
        
        result = []
        for (adult, change_type, accident) in cursor:
            result.append({
                "adult": adult,
                "change_type": change_type,
                "accident": bool(accident)
            })
        return result
