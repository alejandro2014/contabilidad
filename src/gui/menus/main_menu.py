from src.gui.menus.menu_configure import MenuConfigure
from src.gui.menus.menu_expenses import MenuExpenses
from src.gui.menus.menu_view import MenuView


class MainMenu:
    def __init__(self, main_window):
        self.menu_expenses = MenuExpenses(main_window)
        self.menu_view = MenuView(main_window)
        self.menu_configure = MenuConfigure(main_window)