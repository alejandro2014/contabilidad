from src.gui.menus.menu_configure import MenuConfigure
from src.gui.menus.menu_expenses import MenuExpenses
from src.gui.menus.menu_view import MenuView


class MainMenu:
    def __init__(self, main_window, listeners_pool=None):
        self.listeners_pool = listeners_pool

        self.menu_expenses = MenuExpenses(main_window, listeners_pool)
        self.menu_view = MenuView(main_window, listeners_pool)
        self.menu_configure = MenuConfigure(main_window, listeners_pool)