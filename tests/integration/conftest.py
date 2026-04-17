"""Integration-test fixtures: run against a real MariaDB.

Requires env vars DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME.
In CI these are set by the workflow; locally, export them or `docker-compose up -d db` first.
"""
import glob
import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def db_available():
    """Skip integration tests entirely if DB env isn't configured."""
    if not os.getenv("DB_HOST"):
        pytest.skip("DB_HOST not set — skipping integration tests")
    try:
        from app.db import get_connection
        with get_connection() as conn:
            conn.cursor().execute("SELECT 1")
    except Exception as e:
        pytest.skip(f"MariaDB not reachable: {e}")
    return True


@pytest.fixture(scope="session", autouse=True)
def init_schema(db_available):
    """Drop all tables and re-run init_db scripts once per session."""
    from app.db import get_connection

    init_dir = Path(__file__).resolve().parents[2] / "init_db"
    sql_files = sorted(glob.glob(str(init_dir / "*.sql")))

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for tbl in ["diaper_changes", "sleep_sessions", "food_intake", "change_types", "adults", "baby"]:
            cursor.execute(f"DROP TABLE IF EXISTS {tbl}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        for sql_file in sql_files:
            content = Path(sql_file).read_text()
            for stmt in content.split(";"):
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)
        conn.commit()
    yield


@pytest.fixture(autouse=True)
def clean_fact_tables():
    """Wipe transaction tables between each test; keep lookup data."""
    from app.db import get_connection

    yield
    with get_connection() as conn:
        cursor = conn.cursor()
        for tbl in ["diaper_changes", "sleep_sessions", "food_intake"]:
            cursor.execute(f"DELETE FROM {tbl}")
        conn.commit()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
