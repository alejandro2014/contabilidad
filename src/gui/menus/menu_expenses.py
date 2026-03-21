from PySide6.QtCore import QCoreApplication

from src.gui.menus.base_menu import BaseMenu
from src.gui.dialogs.load_file_dialog import LoadFileDialog
from src.gui.screens.ClassifyExpensesScreen import ClassifyExpensesScreen

class MenuExpenses(BaseMenu):
    def __init__(self, main_window, listeners_pool):
        self.listeners_pool = listeners_pool
        
        self.init_menu('expenses', main_window)

    def load_expenses_file(self):
        LoadFileDialog(self.main_window, self.listeners_pool)

    def classify_expenses(self):
        classify_expenses_screen = ClassifyExpensesScreen(self.listeners_pool)
        self.setCentralWidget(classify_expenses_screen)

    def print_report(self):
        return
    
    def exit_app(self):
        QCoreApplication.instance().quit()
