from src.gui.dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog

from src.gui.menus.base_menu import BaseMenu


class MenuConfigure(BaseMenu):
    def __init__(self, main_window):
        self.init_menu('configure', main_window)

    def configure_expense_types(self):
        ConfigureExpensesDialog(self.main_window)

    def configure_classification_rules(self):
        pass
