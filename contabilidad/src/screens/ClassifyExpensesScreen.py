from PySide2.QtWidgets import QVBoxLayout, QWidget

from src.widgets.FilterWidget import FilterWidget

from src.widgets.tables.PendingExpensesTable import PendingExpensesTable

from globals import widgets_pool as wpool

from src.widgets.RootWidget import RootWidget

class ClassifyExpensesScreen(RootWidget):
    def __init__(self):
        super().__init__()

    def init_widgets(self):
        pass

    def get_widgets_from_pool(self):
        self.filter_widget = wpool.get('filter-widget')
        self.pending_expenses_table = wpool.get('pending-expenses-table')

    def create_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.filter_widget)
        layout.addWidget(self.pending_expenses_table)

        self.setLayout(layout)

    def init_widgets(self):
        self.pending_expenses_table.refresh()
        wpool.execute('filter-widget', 'set_visibility_pending')
