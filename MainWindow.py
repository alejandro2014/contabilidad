from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import QMainWindow, QStatusBar

from src.dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog
from src.dialogs.LoadFileDialog import LoadFileDialog

from src.events.ListenersPool import ListenersPool

from src.screens.ClassifyExpensesScreen import ClassifyExpensesScreen
from src.screens.ViewChartsScreen import ViewChartsScreen
from src.screens.ViewExpensesScreen import ViewExpensesScreen

from src.services.ClassifiedExpensesService import ClassifiedExpensesService
from src.services.PendingExpensesService import PendingExpensesService

from src.widgets.StatusBar import StatusBar

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.listeners_pool = ListenersPool()
        self.setWindowTitle('Contabilidad')
        self.resize(1000, 900)

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

        print_report_action = menu_gastos.addAction('Imprimir informe')
        print_report_action.triggered.connect(self.print_report)

        menu_gastos.addSeparator()

        exit_app_action = menu_gastos.addAction('Salir')
        exit_app_action.triggered.connect(self.exit_app)

        menu_gastos = self.menubar.addMenu('Ver')

        view_expenses_table_action = menu_gastos.addAction('Ver tabla')
        view_expenses_table_action.triggered.connect(self.view_expenses_table)

        view_expenses_charts_action = menu_gastos.addAction('Ver graficos')
        view_expenses_charts_action.triggered.connect(self.view_expenses_charts)

        menu_configuracion = self.menubar.addMenu('Configuracion')

        configure_columns_action = menu_configuracion.addAction('Columnas de entrada')
        configure_columns_action.triggered.connect(self.configure_columns)

        configure_expense_types_action = menu_configuracion.addAction('Tipos de gastos')
        configure_expense_types_action.triggered.connect(self.configure_expense_types)

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

    def print_report(self):
        return

    def configure_columns(self):
        return

    def exit_app(self):
        QCoreApplication.instance().quit()
