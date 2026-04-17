from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def fake_db(monkeypatch):
    """Patches app.crud.get_connection with a MagicMock conn.

    Usage:
        def test_something(fake_db):
            fake_db.configure(rows=[...], lastrowid=5)
            ...
            fake_db.cursor.execute.assert_called_once_with(...)
    """

    class FakeDB:
        def __init__(self):
            self.cursor = MagicMock()
            self.cursor.__iter__ = lambda self: iter(self._rows)
            self.cursor._rows = []
            self.cursor.lastrowid = 1
            self.conn = MagicMock()
            self.conn.cursor.return_value = self.cursor

        def configure(self, rows=None, lastrowid=1, execute_raises=None):
            self.cursor._rows = rows or []
            self.cursor.__iter__ = lambda s: iter(s._rows)
            self.cursor.lastrowid = lastrowid
            if execute_raises is not None:
                self.cursor.execute.side_effect = execute_raises

    fake = FakeDB()

    @contextmanager
    def fake_get_connection():
        yield fake.conn

    monkeypatch.setattr("app.crud.get_connection", fake_get_connection)
    return fake
