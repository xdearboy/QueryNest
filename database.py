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
            raise DatabaseError("Похоже, это не база SQLite")
        self.conn = conn

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def tables(self):
        if self.conn is None:
            return []
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()
        return [row[0] for row in rows]

    def columns(self, table):
        if self.conn is None:
            raise DatabaseError("База данных не открыта")
        table = table.replace('"', '""')
        rows = self.conn.execute(f'PRAGMA table_info("{table}")').fetchall()
        if not rows:
            raise DatabaseError("Такой таблицы нет")
        return [row[1] for row in rows]

    def execute(self, sql):
        if self.conn is None:
            raise DatabaseError("База данных не открыта")
        try:
            result = self.conn.execute(sql)
            names = [item[0] for item in result.description] if result.description else []
            rows = result.fetchall() if names else []
            count = len(rows) if names else max(result.rowcount, 0)
            self.conn.commit()
            return names, rows, count
        except sqlite3.DatabaseError as error:
            self.conn.rollback()
            raise DatabaseError(str(error))

    def preview(self, table):
        if self.conn is None:
            raise DatabaseError("База данных не открыта")
        table = table.replace('"', '""')
        try:
            result = self.conn.execute(f'SELECT * FROM "{table}" LIMIT 100')
        except sqlite3.DatabaseError as error:
            raise DatabaseError(str(error))
        names = [item[0] for item in result.description]
        return names, result.fetchall()

