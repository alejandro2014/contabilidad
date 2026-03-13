from src.dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog

class MenuLoader:
    def __init__(self, main_window):
        self.menu_bar = main_window.menuBar()

    def load(self):
        self.load_expenses_submenu()
        self.load_view_submenu()
        self.load_configuration_submenu()

        return self

    def load_expenses_submenu(self):
        menu_gastos = self.menu_bar.addMenu('Gastos')

        load_expenses_file_action = menu_gastos.addAction('Cargar fichero')
        load_expenses_file_action.triggered.connect(self.load_expenses_file)

        classify_expenses_action = menu_gastos.addAction('Clasificar pendientes')
        classify_expenses_action.triggered.connect(self.classify_expenses)

        print_report_action = menu_gastos.addAction('Imprimir informe')
        print_report_action.triggered.connect(self.print_report)

        menu_gastos.addSeparator()

        exit_app_action = menu_gastos.addAction('Salir')
        exit_app_action.triggered.connect(self.exit_app)

    def load_view_submenu(self):
        menu_gastos = self.menu_bar.addMenu('Ver')

        view_expenses_table_action = menu_gastos.addAction('Ver tabla')
        view_expenses_table_action.triggered.connect(self.view_expenses_table)

        view_expenses_charts_action = menu_gastos.addAction('Ver graficos')
        view_expenses_charts_action.triggered.connect(self.view_expenses_charts)

    def load_configuration_submenu(self):
        menu_configuracion = self.menu_bar.addMenu('Configuracion')

        #configure_columns_action = menu_configuracion.addAction('Columnas de entrada')
        #configure_columns_action.triggered.connect(self.configure_columns)

        configure_expense_types_action = menu_configuracion.addAction('Tipos de gastos')
        configure_expense_types_action.triggered.connect(self.configure_expense_types)

        configure_expense_types_action = menu_configuracion.addAction('Reglas de clasificación')
        configure_expense_types_action.triggered.connect(self.configure_classification_rules)


    def init_status_bar(self):
        self.status_bar = StatusBar(self.listeners_pool)
        self.setStatusBar(self.status_bar)

    def load_expenses_file(self):
        load_file_dialog = LoadFileDialog(self, self.listeners_pool)

    def classify_expenses(self):
        classify_expenses_screen = ClassifyExpensesScreen(self.listeners_pool)
        self.setCentralWidget(classify_expenses_screen)

    def view_expenses_table(self):
        view_expenses_screen = ViewExpensesScreen(self.listeners_pool)
        self.setCentralWidget(view_expenses_screen)

    def view_expenses_charts(self):
        view_charts_screen = ViewChartsScreen(self.listeners_pool)
        self.setCentralWidget(view_charts_screen)

    def configure_expense_types(self):
        configure_expenses_dialog = ConfigureExpensesDialog(self)

    def configure_classification_rules(self):
        pass

    def print_report(self):
        return

    def configure_columns(self):
        return

    def exit_app(self):
        QCoreApplication.instance().quit()