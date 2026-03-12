from PySide2.QtCore import QCoreApplication
from PySide2.QtWidgets import QAction, QMenuBar

from src.dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog
from src.dialogs.ConfigureColumnsDialog import ConfigureColumnsDialog
from src.dialogs.LoadFileDialog import LoadFileDialog

from src.misc.KeyGetter import KeyGetter

from src.screens.ClassifyExpensesScreen import ClassifyExpensesScreen
from src.screens.ViewChartsScreen import ViewChartsScreen
from src.screens.ViewExpensesScreen import ViewExpensesScreen

from src.services.ClassifiedExpensesService import ClassifiedExpensesService
from src.services.ExpenseTypesService import ExpenseTypesService
from src.services.PendingExpensesService import PendingExpensesService

from globals import widgets_pool as wpool

class MenuBar(QMenuBar, KeyGetter):
    def __init__(self, main_window):
        QMenuBar.__init__(self)

        self.main_window = main_window

        self.actions = {
            'expenses': {
                'load_file': self.create_action('Cargar fichero', self.load_expenses_file),
                'classify': self.create_action('Clasificar pendientes', self.classify_expenses),
                'exit': self.create_action('Salir', self.exit_app)
            },
            'view': {
                'table': self.create_action('Ver tabla', self.view_expenses_table),
                'charts': self.create_action('Ver graficos', self.view_expenses_charts)
            },
            'configure': {
                'columns': self.create_action('Columnas de entrada', self.configure_columns),
                'categories': self.create_action('Tipos de gastos', self.configure_expense_types)
            }
        }

        self.classified_expenses_service = ClassifiedExpensesService()
        self.expense_types_service = ExpenseTypesService()
        self.pending_expenses_service = PendingExpensesService()

        self.load_options_menu()
        self.refresh()

    def get_widgets_from_pool(self):
        pass

    def create_layout(self):
        pass

    def init_widgets(self):
        pass

    def refresh(self):
        self.refresh_expenses_classify()
        self.refresh_view_table()
        self.refresh_view_charts()

    def refresh_expenses_classify(self):
        pending_expenses_no = self.pending_expenses_service.get_expenses_count()
        expense_types_no = self.expense_types_service.get_expense_types_count()
        condition = (pending_expenses_no > 0 and expense_types_no > 0)

        self.set_enabled('expenses.classify', condition)

    def refresh_view_table(self):
        classified_expenses_no = self.classified_expenses_service.get_expenses_count()
        condition = (classified_expenses_no > 0)

        self.set_enabled('view.table', condition)

    def refresh_view_charts(self):
        classified_expenses_no = self.classified_expenses_service.get_expenses_count()
        condition = (classified_expenses_no > 0)

        self.set_enabled('view.charts', condition)

    def create_action(self, title, action_method):
        return QAction(title, self, triggered=action_method)

    def get_action(self, key):
        return self.value(key, self.actions)

    def set_enabled(self, key, condition):
        action = self.get_action(key)
        action.setEnabled(condition)

    def load_options_menu(self):
        menu_gastos = self.addMenu('Gastos')
        menu_gastos.addAction(self.get_action('expenses.load_file'))
        menu_gastos.addAction(self.get_action('expenses.classify'))
        menu_gastos.addSeparator()
        menu_gastos.addAction(self.get_action('expenses.exit'))

        menu_ver = self.addMenu('Ver')
        menu_ver.addAction(self.get_action('view.table'))
        menu_ver.addAction(self.get_action('view.charts'))

        menu_configuracion = self.addMenu('Configuracion')
        menu_configuracion.addAction(self.get_action('configure.columns'))
        menu_configuracion.addAction(self.get_action('configure.categories'))

    def load_expenses_file(self):
        load_file_dialog = LoadFileDialog(self)

    def classify_expenses(self):
        classify_expenses_screen = ClassifyExpensesScreen(self)
        self.main_window.setCentralWidget(classify_expenses_screen)

    def view_expenses_charts(self):
        self.main_window.view_expenses_charts()

    def view_expenses_table(self):
        view_expenses_screen = ViewExpensesScreen(self)
        self.main_window.setCentralWidget(view_expenses_screen)

    def configure_expense_types(self):
        configure_expenses_dialog = ConfigureExpensesDialog(self)

    def configure_columns(self):
        configure_columns_dialog = ConfigureColumnsDialog(self)

    def exit_app(self):
        QCoreApplication.instance().quit()
