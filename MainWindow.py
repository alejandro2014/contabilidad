from PySide6.QtWidgets import QMainWindow, QStatusBar

from src.events.ListenersPool import ListenersPool

#from src.widgets.StatusBar import StatusBar

from src.menu_configure import MenuConfigure
from src.menu_expenses import MenuExpenses
from src.menu_view import MenuView

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.listeners_pool = ListenersPool()
        self.setWindowTitle('Contabilidad')
        self.resize(1000, 900)

        self.menu_expenses = MenuExpenses(self)
        self.menu_view = MenuView(self)
        self.menu_configure = MenuConfigure(self)

        #self.init_status_bar()

    def init_status_bar(self):
        self.status_bar = StatusBar(self.listeners_pool)
        self.setStatusBar(self.status_bar)
