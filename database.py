import os
import sqlite3


class DatabaseError(Exception):
    pass


class Database:
    """Управление подключением к SQLite базе и выполнение запросов."""

    def __init__(self):
        self.conn = None

    def open(self, path):
        """Открыть SQLite базу по пути.

        Аргументы:
            path: путь к файлу .db, .sqlite или .sqlite3

        Вызывает DatabaseError если файл не существует или не SQLite база.
        """
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
        """Закрыть соединение с базой."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def tables(self):
        """Получить список имён таблиц (без служебных таблиц SQLite).

        Возвращает список строк, отсортирован по алфавиту.
        Возвращает пустой список если база не открыта.
        """
        if self.conn is None:
            return []
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()
        return [row[0] for row in rows]

    def columns(self, table):
        """Получить список имён столбцов таблицы.

        Аргументы:
            table: имя таблицы

        Возвращает список строк — имена столбцов.
        Вызывает DatabaseError если база не открыта или таблица не существует.
        """
        if self.conn is None:
            raise DatabaseError("База данных не открыта")
        table = table.replace('"', '""')
        rows = self.conn.execute(f'PRAGMA table_info("{table}")').fetchall()
        if not rows:
            raise DatabaseError("Такой таблицы нет")
        return [row[1] for row in rows]

    def execute(self, sql):
        """Выполнить SQL-запрос (SELECT, INSERT, UPDATE, DELETE и т.д.).

        Аргументы:
            sql: SQL-запрос в виде строки

        Возвращает кортеж (names, rows, count):
        - names: список имён столбцов (для SELECT, иначе пусто)
        - rows: список кортежей — строки результата (для SELECT, иначе пусто)
        - count: количество вернулось строк (SELECT) или изменённых строк (INSERT/UPDATE/DELETE)

        Вызывает DatabaseError если база не открыта или SQL содержит ошибку.
        """
        if self.conn is None:
            raise DatabaseError("База данных не открыта")
        try:
            result = self.conn.execute(sql)
            names = (
                [item[0] for item in result.description] if result.description else []
            )
            rows = result.fetchall() if names else []
            count = len(rows) if names else max(result.rowcount, 0)
            self.conn.commit()
            return names, rows, count
        except sqlite3.DatabaseError as error:
            self.conn.rollback()
            raise DatabaseError(str(error))

    def preview(self, table):
        """Получить первые 100 строк таблицы.

        Аргументы:
            table: имя таблицы

        Возвращает кортеж (names, rows):
        - names: список имён столбцов
        - rows: список кортежей (максимум 100 строк)

        Вызывает DatabaseError если база не открыта или таблица не существует.
        """
        if self.conn is None:
            raise DatabaseError("База данных не открыта")
        table = table.replace('"', '""')
        try:
            result = self.conn.execute(f'SELECT * FROM "{table}" LIMIT 100')
        except sqlite3.DatabaseError as error:
            raise DatabaseError(str(error))
        names = [item[0] for item in result.description]
        return names, result.fetchall()
