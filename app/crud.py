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
            SELECT dc.change_time, a.name, ct.change_type, dc.accident
            FROM diaper_changes dc
            JOIN adults a ON dc.adult_id = a.adult_id
            JOIN change_types ct ON dc.change_type_id = ct.change_id
            ORDER BY dc.change_time DESC
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
        
        result = []
        for (time, adult, type, accident) in cursor:
            result.append({
                "time": time,
                "adult": adult,
                "type": type,
                "accident": bool(accident)
            })
        return result


if __name__ == "__main__":
    print("--- STARTAR TEST AV CRUD ---")
    
    try:
        test_change = DiaperChangeCreate(
            adult_id=1, 
            change_type_id=1, 
            accident=False
        )
        
        print("Testar att spara ett blöjbyte...")
        res = create_diaper_change(test_change)
        print(f"Resultat från databasen: {res}")
        
    except Exception as e:
        print(f"Ett fel uppstod under testet: {e}")
