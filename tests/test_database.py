import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import Database, DatabaseError


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER)")
    conn.executemany(
        "INSERT INTO users (name, age) VALUES (?, ?)",
        [("Anna", 15), ("Ivan", 16), ("Olga", 15)],
    )
    conn.commit()
    conn.close()
    return str(path)


def test_open_valid_file(db_path):
    db = Database()
    db.open(db_path)
    assert db.conn is not None
    db.close()


def test_open_missing_file(tmp_path):
    db = Database()
    with pytest.raises(DatabaseError):
        db.open(str(tmp_path / "nope.db"))


def test_open_text_file(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("это не база данных, просто текст " * 10)
    db = Database()
    with pytest.raises(DatabaseError):
        db.open(str(path))
    assert db.conn is None


def test_close(db_path):
    db = Database()
    db.open(db_path)
    db.close()
    assert db.conn is None
