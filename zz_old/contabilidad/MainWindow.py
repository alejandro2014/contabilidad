from PySide6.QtWidgets import QMainWindow, QStatusBar
from PySide6.QtGui import QColor

from src.dialogs.LoadFileDialog import LoadFileDialog

from src.screens.ClassifyExpensesScreen import ClassifyExpensesScreen
from src.screens.EmptyScreen import EmptyScreen
from src.screens.ViewChartsScreen import ViewChartsScreen
from src.screens.ViewExpensesScreen import ViewExpensesScreen

from src.services.ClassifiedExpensesService import ClassifiedExpensesService
from src.services.PendingExpensesService import PendingExpensesService

from src.widgets.MenuBar import MenuBar

from src.widgets.Summatory import Summatory
from src.widgets.charts.BarChart import BarChart
from src.widgets.charts.PieChart import PieChart

from globals import widgets_pool as wpool

from src.widgets.Classifier import Classifier
from src.widgets.DateFilter import DateFilter
from src.widgets.FilterWidget import FilterWidget
from src.widgets.SecondaryFilters import SecondaryFilters
from src.widgets.TextFilter import TextFilter

from src.widgets.tables.PendingExpensesTable import PendingExpensesTable

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Gestor de contabilidad 0.1')
        self.resize(1400, 1000)

        self.classified_expenses_service = ClassifiedExpensesService()
        self.pending_expenses_service = PendingExpensesService()

        self.init_widgets_pool()

        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)

        self.init_status_bar()

        classified_expenses_no = self.classified_expenses_service.get_expenses_count()

        if classified_expenses_no == 0:
            self.view_empty_panel()
        else:
            self.view_expenses_charts()

    def init_widgets_pool(self):
        wpool.add('pie-chart', PieChart())
        wpool.add('sum-text', Summatory())

        wpool.add('classifier', Classifier(True))
        wpool.add('date-filter', DateFilter())
        wpool.add('filter-widget', FilterWidget('charts'))
        wpool.add('menubar', MenuBar(self))
        wpool.add('secondary-filters', SecondaryFilters())
        wpool.add('text-filter', TextFilter())

        wpool.add('classify-expenses-screen', ClassifyExpensesScreen())
        wpool.add('empty-screen', EmptyScreen())
        wpool.add('view-charts-screen', ViewChartsScreen())
        wpool.add('view-expenses-screen', ViewExpensesScreen())

        wpool.add('pending-expenses-table', PendingExpensesTable())

        wpool.add('savings-chart', BarChart("Ahorro", 'savings', QColor(50, 200, 250)))
        wpool.add('incomes-chart', BarChart("Ingresos", 'incomes', QColor(150, 50, 50)))

        wpool.init()

    def view_empty_panel(self):
        empty_screen = wpool.get('empty-screen')
        self.setCentralWidget(empty_screen)

    def view_expenses_charts(self):
        view_charts_screen = wpool.get('view-charts-screen')
        self.setCentralWidget(view_charts_screen)

    def init_status_bar(self):
        pending = self.pending_expenses_service.get_expenses_count()
        classified = self.classified_expenses_service.get_expenses_count()

        self.status_bar = QStatusBar()
        self.status_bar.showMessage('Pendientes: ' + str(pending) + ', Clasificados: ' + str(classified), 0)
        self.setStatusBar(self.status_bar)
