from PySide6.QtWidgets import QMainWindow, QStatusBar

from src.events.ListenersPool import ListenersPool

#from src.widgets.StatusBar import StatusBar

from src.menu_configure import MenuConfigure
from src.menu_expenses import MenuExpenses
from src.menu_view import MenuView

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.listeners_pool = ListenersPool()
        self.setWindowTitle('Contabilidad')
        self.resize(1000, 900)

        self.menu_expenses = MenuExpenses(self)
        self.menu_view = MenuView(self)
        self.menu_configure = MenuConfigure(self)

        self.menubar = self.menuBar()

        self.load_options_menu()

        #self.init_status_bar()
        
    def load_options_menu(self):
        self.load_expenses_submenu()
        self.load_view_submenu()
        self.load_configuration_submenu()

    def load_expenses_submenu(self):
        menu_gastos = self.menubar.addMenu('Gastos')

        load_expenses_file_action = menu_gastos.addAction('Cargar fichero')
        load_expenses_file_action.triggered.connect(self.menu_expenses.load_expenses_file)

        classify_expenses_action = menu_gastos.addAction('Clasificar pendientes')
        classify_expenses_action.triggered.connect(self.menu_expenses.classify_expenses)

        print_report_action = menu_gastos.addAction('Imprimir informe')
        print_report_action.triggered.connect(self.menu_expenses.print_report)

        menu_gastos.addSeparator()

        exit_app_action = menu_gastos.addAction('Salir')
        exit_app_action.triggered.connect(self.menu_expenses.exit_app)

    def load_view_submenu(self):
        menu_gastos = self.menubar.addMenu('Ver')

        view_expenses_table_action = menu_gastos.addAction('Ver tabla')
        view_expenses_table_action.triggered.connect(self.menu_view.view_expenses_table)

        view_expenses_charts_action = menu_gastos.addAction('Ver graficos')
        view_expenses_charts_action.triggered.connect(self.menu_view.view_expenses_charts)

    def load_configuration_submenu(self):
        menu_configuracion = self.menubar.addMenu('Configuracion')

        configure_expense_types_action = menu_configuracion.addAction('Tipos de gastos')
        configure_expense_types_action.triggered.connect(self.menu_configure.configure_expense_types)

        configure_expense_types_action = menu_configuracion.addAction('Reglas de clasificación')
        configure_expense_types_action.triggered.connect(self.menu_configure.configure_classification_rules)


    def init_status_bar(self):
        self.status_bar = StatusBar(self.listeners_pool)
        self.setStatusBar(self.status_bar)
