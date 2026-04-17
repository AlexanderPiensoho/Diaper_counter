from unittest.mock import MagicMock

import pytest

from app import db


def test_get_db_config_reads_env(monkeypatch):
    monkeypatch.setenv("DB_HOST", "myhost")
    monkeypatch.setenv("DB_PORT", "3307")
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_NAME", "n")

    cfg = db.get_db_config()
    assert cfg == {
        "host": "myhost",
        "port": 3307,
        "user": "u",
        "password": "p",
        "database": "n",
    }


def test_get_connection_yields_and_closes(monkeypatch):
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_PORT", "3306")
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_NAME", "n")

    mock_conn = MagicMock()
    monkeypatch.setattr("app.db.mariadb.connect", lambda **kwargs: mock_conn)

    with db.get_connection() as conn:
        assert conn is mock_conn
    mock_conn.close.assert_called_once()


def test_get_connection_closes_even_on_exception(monkeypatch):
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_PORT", "3306")
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_NAME", "n")

    mock_conn = MagicMock()
    monkeypatch.setattr("app.db.mariadb.connect", lambda **kwargs: mock_conn)

    with pytest.raises(RuntimeError):
        with db.get_connection():
            raise RuntimeError("boom")
    mock_conn.close.assert_called_once()
