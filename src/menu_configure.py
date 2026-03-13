from src.dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog

class MenuConfigure:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menubar = self.main_window.menuBar()

        menu_configuracion = self.menubar.addMenu('Configuracion')

        configure_expense_types_action = menu_configuracion.addAction('Tipos de gastos')
        configure_expense_types_action.triggered.connect(self.configure_expense_types)

        configure_expense_types_action = menu_configuracion.addAction('Reglas de clasificación')
        configure_expense_types_action.triggered.connect(self.configure_classification_rules)

    def configure_expense_types(self):
        ConfigureExpensesDialog(self.main_window)

    def configure_classification_rules(self):
        pass
