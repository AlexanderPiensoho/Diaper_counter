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

