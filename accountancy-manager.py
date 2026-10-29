import sys
from PySide6.QtWidgets import QApplication

from MainWindow import MainWindow
from src.logger import configure_logging

if __name__ == "__main__":
    configure_logging()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
