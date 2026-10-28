import os

# The widgets are tested without opening any window
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication

def get_app():
    # Qt allows a single application per process, shared by all the widget tests
    return QApplication.instance() or QApplication([])
