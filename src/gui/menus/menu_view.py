from src.gui.screens.view_charts_screen import ViewChartsScreen
from src.gui.screens.view_expenses_screen import ViewExpensesScreen

#from src.services.ClassifiedExpensesService import ClassifiedExpensesService
#from src.services.PendingExpensesService import PendingExpensesService

"""
self.view_expenses_table()
self.view_expenses_charts()
"""

from src.gui.menus.base_menu import BaseMenu


class MenuView(BaseMenu):
    def __init__(self, main_window, listeners_pool):
        self.listeners_pool = listeners_pool
        self.init_menu('view', main_window)

    def view_expenses_table(self):
        view_expenses_screen = ViewExpensesScreen(self.listeners_pool)
        self.setCentralWidget(view_expenses_screen)

    def view_expenses_charts(self):
        view_charts_screen = ViewChartsScreen(self.listeners_pool)
        self.setCentralWidget(view_charts_screen)
