import os
import sqlite3


class DatabaseError(Exception):
    pass


class Database:
    def __init__(self):
        self.conn = None

    def open(self, path):
        if not os.path.isfile(path):
            raise DatabaseError("Файл не найден")
        self.close()
        try:
            conn = sqlite3.connect(path)
            conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        except sqlite3.DatabaseError:
            raise DatabaseError("Файл не является базой SQLite")
        self.conn = conn

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
