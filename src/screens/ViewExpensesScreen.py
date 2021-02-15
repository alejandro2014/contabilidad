from PySide2.QtWidgets import QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode
from src.events.ListenersPool import ListenersPool

from src.widgets.FilterWidget import FilterWidget

from src.widgets.tables.ClassifiedExpensesTable import ClassifiedExpensesTable

class ViewExpensesScreen(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(ViewExpensesScreen, self).__init__(*args, **kwargs)

        self.listeners_pool = listeners_pool
        ListenerNode.__init__(self, 'view-expenses-screen', self.listeners_pool)

        self.classified_expenses_table = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.filter_widget = FilterWidget('classified', listeners_pool)
        self.layout.addWidget(self.filter_widget)

        self.add_table('expenses_raw')
        self.send_event('sum-text', 'show_records_no')

    def add_table(self, table_type):
        if self.classified_expenses_table != None:
            self.layout.removeWidget(self.classified_expenses_table)

        self.classified_expenses_table = ClassifiedExpensesTable(self.listeners_pool, table_type)
        self.classified_expenses_table.refresh_rows()
        self.layout.addWidget(self.classified_expenses_table)
