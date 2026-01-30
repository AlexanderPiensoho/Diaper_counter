import mariadb
import sys
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

def get_db_config():
    return {
        'host': os.getenv("DB_HOST"),
        'port': int(os.getenv('DB_PORT')),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
        }

@contextmanager
def get_connection():
    conn = mariadb.connect(**get_db_config())
    try:
        yield conn 
    finally:
        conn.close()


def insert_diaper_changes():
    conn = None
    try:
        print("connecting to Mariadb...")
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT adult_id, name FROM adults")
        adults = cursor.fetchall()
        print("---Vem byter blöjan?---")

        for a_id, name in adults:
            print(f"{a_id}. {name}")

        adult_id = int(input("Välj ID: ")) 


        cursor.execute("SELECT change_id, change_type FROM change_types")
        types = cursor.fetchall()
        print("--kiss, bajs eller rutinbyte?---")

        for c_id, c_type in types:
            print(f"{c_id}. {c_type}")
        type_id = int(input("Välj ID: "))


        accident_input = input("Skedde det en olycka under blöjbytet?(y/n): ").lower()
        accident = 1 if accident_input == "y" else 0



        insert_change = "INSERT INTO diaper_changes (baby_id, change_type_id, accident, adult_id) VALUES (?,?,?,?)"
        
        cursor.execute(insert_change, (1, type_id, accident, adult_id))
        conn.commit()
        print("Blöjbyte registrerat!")

    except mariadb.Error as e:
        print(f"Error inserting data : {e}")
        if conn:
            conn.rollback()
    except ValueError:
        print("du måste välja ett ID")
    finally:
        if conn:
            conn.close()

