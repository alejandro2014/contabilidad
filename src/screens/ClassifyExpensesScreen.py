from PySide2.QtWidgets import QVBoxLayout, QWidget

from src.events.ListenersPool import ListenersPool

from src.widgets.FilterWidget import FilterWidget

from src.widgets.tables.PendingExpensesTable import PendingExpensesTable

class ClassifyExpensesScreen(QWidget):
    def __init__(self, listeners_pool):
        super(ClassifyExpensesScreen, self).__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.filter_widget = FilterWidget('pending', listeners_pool)
        self.pending_expenses_table = PendingExpensesTable(listeners_pool)

        layout.addWidget(self.filter_widget)
        layout.addWidget(self.pending_expenses_table)

        self.pending_expenses_table.refresh_rows()
