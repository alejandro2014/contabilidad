import sys
from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow

if __name__ == "__main__":
    print("[INFO] -------- Program started --------")

    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())
