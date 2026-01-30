import mariadb
import sys
import os
from dotenv import load_dotenv

load_dotenv()

change_id_counter = 1
db_config = {
        'host': os.getenv('host'),
        'port': int(os.getenv('port')),
        'user': os.getenv('user'),
        'password': os.getenv('password'),
        'database': 'diaper_counter'
        }

def insert_diaper_changes():
    conn = None
    cursor = None
    try:
        print("connecting to Mariadb...")
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()
        
        baby_id = 1
        accident = input("accident (y/n): ").lower()
        if accident == "y":
            accident = 1
        else:
            accident = 0

        adult_id = input("""Adult_id 
                          1. Alexander
                          2. Elin
                         """)

        insert_change = "INSERT INTO diaper_changes (baby_id, accident, adult_id) VALUES (?,?,?)"
        
        cursor.execute(insert_change, (baby_id, accident, adult_id))
        conn.commit()
        print(f"Diaper change done by {adult_id}")

    except mariadb.Error as e:
        print(f"Error inserting data : {e}")
        if conn:
            conn.rollback()
    except ValueError:
        print("You must use a number for ID fields")
    finally:
        if conn:
            conn.close()

