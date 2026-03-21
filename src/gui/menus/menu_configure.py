from src.gui.dialogs.configure_expenses_dialog import ConfigureExpensesDialog
from src.gui.dialogs.configure_rules_dialog import ConfigureRulesDialog
from src.gui.dialogs.add_rule_dialog import AddRuleDialog

from src.gui.menus.base_menu import BaseMenu


class MenuConfigure(BaseMenu):
    def __init__(self, main_window, listeners_pool):
        self.init_menu('configure', main_window)

    def configure_expense_types(self):
        ConfigureExpensesDialog(self.main_window)

    def configure_classification_rules(self):
        #ConfigureRulesDialog(self.main_window)
        AddRuleDialog(self.main_window)
