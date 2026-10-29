from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMainWindow, QStatusBar

from src.dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog
from src.dialogs.ConfigureRulesDialog import ConfigureRulesDialog
from src.dialogs.InfoDialog import InfoDialog
from src.dialogs.LoadFileDialog import LoadFileDialog

from src.events.ListenersPool import ListenersPool

from src.screens.CashflowWindow import CashflowWindow
from src.screens.ClassifyExpensesScreen import ClassifyExpensesScreen
from src.screens.ViewChartsScreen import ViewChartsScreen
from src.screens.ViewExpensesScreen import ViewExpensesScreen

from src.services.expenses_service import ExpensesService

from DateConverter import DateConverter

from src.widgets.StatusBar import StatusBar

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.listeners_pool = ListenersPool()
        self.cashflow_window = None
        self.setWindowTitle('Contabilidad')
        self.resize(1300, 1000)

        self.menubar = self.menuBar()

        self.load_options_menu()
        self.init_status_bar()
        #self.view_expenses_table()
        self.view_expenses_charts()

    def load_options_menu(self):
        menu_gastos = self.menubar.addMenu('Gastos')

        load_expenses_file_action = menu_gastos.addAction('Cargar fichero')
        load_expenses_file_action.triggered.connect(self.load_expenses_file)

        classify_expenses_action = menu_gastos.addAction('Clasificar pendientes')
        classify_expenses_action.triggered.connect(self.classify_expenses)

        menu_gastos.addSeparator()

        exit_app_action = menu_gastos.addAction('Salir')
        exit_app_action.triggered.connect(self.exit_app)

        menu_gastos = self.menubar.addMenu('Ver')

        view_expenses_table_action = menu_gastos.addAction('Ver tabla')
        view_expenses_table_action.triggered.connect(self.view_expenses_table)

        view_expenses_charts_action = menu_gastos.addAction('Ver graficos')
        view_expenses_charts_action.triggered.connect(self.view_expenses_charts)

        view_cashflow_action = menu_gastos.addAction('Flujo de caja')
        view_cashflow_action.triggered.connect(self.view_cashflow)

        menu_gastos.addSeparator()

        view_date_range_action = menu_gastos.addAction('Rango de fechas')
        view_date_range_action.triggered.connect(self.view_date_range)

        menu_configuracion = self.menubar.addMenu('Configuracion')

        configure_expense_types_action = menu_configuracion.addAction('Tipos de gastos')
        configure_expense_types_action.triggered.connect(self.configure_expense_types)

        configure_rules_action = menu_configuracion.addAction('Reglas de clasificación')
        configure_rules_action.triggered.connect(self.configure_rules)

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

    def view_cashflow(self):
        # Only one cashflow window, brought to the front if it is already open
        if self.cashflow_window is None:
            self.cashflow_window = CashflowWindow(self)
        else:
            self.cashflow_window.refresh()

        self.cashflow_window.show()
        self.cashflow_window.raise_()
        self.cashflow_window.activateWindow()

    def view_date_range(self):
        date_range = ExpensesService().get_expenses_date_range()

        lines = [
            self.date_range_text('Clasificados', date_range['classified']),
            self.date_range_text('Pendientes', date_range['pending'])
        ]

        InfoDialog(self, title = 'Rango de fechas', message = '\n\n'.join(lines))

    def date_range_text(self, label, info):
        if info is None:
            return f'{label}: sin gastos'

        date_converter = DateConverter()
        min_date = date_converter.format_pretty(info['min_date'])
        max_date = date_converter.format_pretty(info['max_date'])

        return f'{label} ({info["count"]} gastos)\n  Mínimo: {min_date}\n  Máximo: {max_date}'

    def configure_expense_types(self):
        configure_expenses_dialog = ConfigureExpensesDialog(self, self.listeners_pool)

    def configure_rules(self):
        configure_rules_dialog = ConfigureRulesDialog(self)

    def exit_app(self):
        QCoreApplication.instance().quit()
