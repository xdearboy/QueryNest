from PyQt6.QtWidgets import (
    QFileDialog,
    QListWidget,
    QMainWindow,
    QMessageBox,
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
        self.setWindowTitle("QueryNest")
        self.resize(900, 600)

        self.open_button = QPushButton("Открыть базу")
        self.tables_list = QListWidget()
        self.data_table = QTableWidget()

        splitter = QSplitter()
        splitter.addWidget(self.tables_list)
        splitter.addWidget(self.data_table)

        layout = QVBoxLayout()
        layout.addWidget(self.open_button)
        layout.addWidget(splitter)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.statusBar().showMessage("База не открыта")

        self.open_button.clicked.connect(self.open_file)
        self.tables_list.currentTextChanged.connect(self.show_table)

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
            self.load_tables()
            self.statusBar().showMessage(path)
        except DatabaseError as error:
            self.show_error(str(error))

    def load_tables(self):
        self.tables_list.clear()
        self.tables_list.addItems(self.db.tables())

    def show_table(self, name):
        if not name:
            return

        try:
            names, rows = self.db.preview(name)
        except DatabaseError as error:
            self.show_error(str(error))
            return

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

        self.statusBar().showMessage(f"{name}: {len(rows)} строк")

    def show_error(self, text):
        self.statusBar().showMessage(text)
        QMessageBox.warning(self, "Ошибка", text)
