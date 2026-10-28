import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import Database, DatabaseError


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_path = ""
        self.setWindowTitle("QueryNest")
        self.resize(950, 650)

        self.tables_list = QListWidget()
        self.query_edit = QPlainTextEdit()
        self.query_edit.setPlaceholderText("Введите SQL-запрос, например: SELECT * FROM ...")
        self.run_button = QPushButton("Выполнить")
        self.data_table = QTableWidget()

        self.setup_menu()
        self.setup_ui()
        self.statusBar().showMessage("База не открыта")

    def setup_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Файл")

        open_action = QAction("Открыть базу...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def setup_ui(self):
        left_layout = QVBoxLayout()
        open_button = QPushButton("Открыть базу")
        open_button.clicked.connect(self.open_file)
        left_layout.addWidget(open_button)
        left_layout.addWidget(QLabel("Таблицы:"))
        left_layout.addWidget(self.tables_list)

        left_panel = QWidget()
        left_panel.setLayout(left_layout)

        query_top_bar = QHBoxLayout()
        query_top_bar.addWidget(QLabel("SQL-запрос (Ctrl+Enter):"))
        query_top_bar.addStretch()
        query_top_bar.addWidget(self.run_button)

        query_layout = QVBoxLayout()
        query_layout.addLayout(query_top_bar)
        query_layout.addWidget(self.query_edit)

        query_panel = QWidget()
        query_panel.setLayout(query_layout)

        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.addWidget(query_panel)
        right_splitter.addWidget(self.data_table)
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 3)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 4)

        self.setCentralWidget(main_splitter)

        self.run_button.clicked.connect(self.run_query)
        self.tables_list.currentTextChanged.connect(self.on_table_clicked)

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self.run_query)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть базу",
            "",
            "SQLite (*.db *.sqlite *.sqlite3)",
        )
        if not path:
            return

        try:
            self.db.open(path)
            self.current_path = path
            self.load_tables()
            filename = os.path.basename(path)
            self.statusBar().showMessage(f"Открыта база: {filename}")
        except DatabaseError as error:
            self.show_error(str(error))

    def load_tables(self):
        self.tables_list.clear()
        self.tables_list.addItems(self.db.tables())

    def on_table_clicked(self, name):
        if not name:
            return

        try:
            names, rows = self.db.preview(name)
        except DatabaseError as error:
            self.show_error(str(error))
            return

        self.show_result(names, rows)
        self.statusBar().showMessage(f"Таблица '{name}': {len(rows)} строк")

    def run_query(self):
        sql = self.query_edit.toPlainText().strip()
        if not sql:
            self.statusBar().showMessage("Введите SQL-запрос")
            return

        if not self.current_path:
            self.show_error("Сначала откройте базу данных")
            return

        try:
            names, rows, count = self.db.execute(sql)
        except DatabaseError as error:
            self.show_error(str(error))
            return

        if names:
            self.show_result(names, rows)
            self.statusBar().showMessage(f"Выполнено строк: {len(rows)}")
        else:
            self.show_result([], [])
            self.load_tables()
            self.statusBar().showMessage(f"Запрос выполнен. Изменено строк: {count}")

    def show_result(self, names, rows):
        self.data_table.clear()
        self.data_table.setColumnCount(len(names))
        self.data_table.setHorizontalHeaderLabels(names)
        self.data_table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                text = "NULL" if value is None else str(value)
                self.data_table.setItem(
                    row_index,
                    column_index,
                    QTableWidgetItem(text),
                )

    def show_error(self, text):
        self.statusBar().showMessage(f"Ошибка: {text}")
        QMessageBox.warning(self, "Ошибка", text)
