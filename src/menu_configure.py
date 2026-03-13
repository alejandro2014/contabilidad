from src.dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog

class MenuConfigure:
    def __init__(self, main_window):
        self.main_window = main_window

    def configure_expense_types(self):
        ConfigureExpensesDialog(self.main_window)

    def configure_classification_rules(self):
        pass
