#from src.screens.ViewChartsScreen import ViewChartsScreen
#from src.screens.ViewExpensesScreen import ViewExpensesScreen

#from src.services.ClassifiedExpensesService import ClassifiedExpensesService
#from src.services.PendingExpensesService import PendingExpensesService

"""
self.view_expenses_table()
self.view_expenses_charts()
"""
class MenuView:
    def __init__(self, main_window):
        self.main_window = main_window

    def view_expenses_table(self):
        view_expenses_screen = ViewExpensesScreen(self.listeners_pool)
        self.setCentralWidget(view_expenses_screen)

    def view_expenses_charts(self):
        view_charts_screen = ViewChartsScreen(self.listeners_pool)
        self.setCentralWidget(view_charts_screen)
