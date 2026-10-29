from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMainWindow

from src.config.settings import app_settings

from src.dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog
from src.dialogs.ConfigureRulesDialog import ConfigureRulesDialog
from src.dialogs.InfoDialog import InfoDialog
from src.dialogs.LoadFileDialog import LoadFileDialog

from src.events.ListenerNode import ListenerNode
from src.events.ListenersPool import ListenersPool

from src.screens.CashflowWindow import CashflowWindow
from src.screens.ClassifyExpensesScreen import ClassifyExpensesScreen
from src.screens.ViewChartsScreen import ViewChartsScreen
from src.screens.ViewExpensesScreen import ViewExpensesScreen

from src.services.expenses_service import ExpensesService

from DateConverter import DateConverter

from src.widgets.StatusBar import StatusBar

class MainWindow(QMainWindow, ListenerNode):
    CLASSIFY_EXPENSES_TEXT = 'Clasificar pendientes'

    # Settings kept between sessions: size and place of the window, and the last screen
    GEOMETRY_SETTING = 'main_window/geometry'
    SCREEN_SETTING = 'main_window/screen'

    def __init__(self):
        super(MainWindow, self).__init__()

        self.listeners_pool = ListenersPool()
        ListenerNode.__init__(self, 'main-window', self.listeners_pool)

        self.cashflow_window = None
        self.setWindowTitle('Contabilidad')
        self.resize(1300, 1000)
        self.restore_geometry()

        self.menubar = self.menuBar()

        self.load_options_menu()
        # The status bar sets the number of pending expenses in the menu, so it goes after it
        self.init_status_bar()
        self.restore_screen()

    def restore_geometry(self):
        geometry = app_settings().value(self.GEOMETRY_SETTING)

        if geometry is not None:
            self.restoreGeometry(geometry)

    def restore_screen(self):
        screens = {
            'charts': self.view_expenses_charts,
            'table': self.view_expenses_table,
            'classify': self.classify_expenses
        }

        # The dashboard when there is no screen saved yet
        screens.get(app_settings().value(self.SCREEN_SETTING), self.view_expenses_charts)()

    def save_screen(self, screen):
        app_settings().setValue(self.SCREEN_SETTING, screen)

    def save_geometry(self):
        app_settings().setValue(self.GEOMETRY_SETTING, self.saveGeometry())

    def closeEvent(self, event):
        self.save_geometry()
        super().closeEvent(event)

    def load_options_menu(self):
        menu_gastos = self.menubar.addMenu('Gastos')

        self.add_action(menu_gastos, 'Cargar fichero', self.load_expenses_file, QKeySequence.StandardKey.Open)
        self.classify_expenses_action = self.add_action(menu_gastos, self.CLASSIFY_EXPENSES_TEXT, self.classify_expenses, 'Ctrl+3')

        menu_gastos.addSeparator()

        self.add_action(menu_gastos, 'Salir', self.exit_app, 'Ctrl+Q')

        menu_ver = self.menubar.addMenu('Ver')

        self.add_action(menu_ver, 'Ver gráficos', self.view_expenses_charts, 'Ctrl+1')
        self.add_action(menu_ver, 'Ver tabla', self.view_expenses_table, 'Ctrl+2')
        self.add_action(menu_ver, 'Flujo de caja', self.view_cashflow, 'Ctrl+4')

        menu_ver.addSeparator()

        self.add_action(menu_ver, 'Rango de fechas', self.view_date_range)

        menu_configuracion = self.menubar.addMenu('Configuración')

        self.add_action(menu_configuracion, 'Tipos de gastos', self.configure_expense_types)
        self.add_action(menu_configuracion, 'Reglas de clasificación', self.configure_rules)

    def add_action(self, menu, text, slot, shortcut = None):
        action = menu.addAction(text)
        action.triggered.connect(slot)

        if shortcut is not None:
            action.setShortcut(QKeySequence(shortcut))

        return action

    def set_pending_count(self, pending):
        text = self.CLASSIFY_EXPENSES_TEXT if pending == 0 else f'{self.CLASSIFY_EXPENSES_TEXT} ({pending})'
        self.classify_expenses_action.setText(text)

    def init_status_bar(self):
        self.status_bar = StatusBar(self.listeners_pool)
        self.setStatusBar(self.status_bar)

    def load_expenses_file(self):
        load_file_dialog = LoadFileDialog(self, self.listeners_pool)

    def classify_expenses(self):
        classify_expenses_screen = ClassifyExpensesScreen(self.listeners_pool)
        self.setCentralWidget(classify_expenses_screen)
        self.save_screen('classify')

    def view_expenses_table(self):
        self.open_expenses_table(None)

    def open_expenses_table(self, filter):
        # From a chart of the dashboard, with the filter of the movements behind it
        view_expenses_screen = ViewExpensesScreen(self.listeners_pool, filter)
        self.setCentralWidget(view_expenses_screen)
        self.save_screen('table')

    def view_expenses_charts(self):
        view_charts_screen = ViewChartsScreen(self.listeners_pool)
        self.setCentralWidget(view_charts_screen)
        self.save_screen('charts')

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
        # Quitting doesn't close the window, so its size is saved here
        self.save_geometry()
        QCoreApplication.instance().quit()
