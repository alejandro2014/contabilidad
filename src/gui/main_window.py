from PySide6.QtWidgets import QMainWindow

from src.events.ListenersPool import ListenersPool

from src.gui.widgets.StatusBar import StatusBar

from src.gui.menus.main_menu import MainMenu

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.listeners_pool = ListenersPool()
        self.setWindowTitle('Contabilidad')
        self.resize(1000, 900)

        self.main_menu = MainMenu(self)

        self.init_status_bar()

    def init_status_bar(self):
        self.status_bar = StatusBar(self.listeners_pool)
        self.setStatusBar(self.status_bar)
