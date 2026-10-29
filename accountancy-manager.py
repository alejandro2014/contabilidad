import sys
from PySide6.QtWidgets import QApplication

from MainWindow import MainWindow
from src.config.settings import init_settings
from src.dao.SqliteConnector import SqliteConnector
from src.logger import configure_logging

if __name__ == "__main__":
    configure_logging()
    init_settings()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    exit_code = app.exec()
    SqliteConnector.shared().close()

    sys.exit(exit_code)
