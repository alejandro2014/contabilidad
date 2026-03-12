from PySide2.QtWidgets import QVBoxLayout, QWidget

from src.widgets.FilterWidget import FilterWidget

from src.widgets.tables.ClassifiedExpensesTable import ClassifiedExpensesTable

from globals import widgets_pool as wpool

from src.widgets.RootWidget import RootWidget

# TODO Refactor layout
class ViewExpensesScreen(RootWidget):
    def __init__(self):
        super().__init__()

        self.classified_expenses_table = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.filter_widget = wpool.get('filter-widget')
        self.layout.addWidget(self.filter_widget)

        self.add_table('expenses_raw')

        filter = self.filter_widget.filter

        self.classified_expenses_table.refresh(filter)
        wpool.execute('filter-widget', 'set_visibility_classified')

    def add_table(self, table_type):
        if self.classified_expenses_table:
            self.layout.removeWidget(self.classified_expenses_table)

        self.classified_expenses_table = ClassifiedExpensesTable(table_type)
        self.classified_expenses_table.refresh()
        self.layout.addWidget(self.classified_expenses_table)

    def get_widgets_from_pool(self):
        pass

    def create_layout(self):
        pass

    def init_widgets(self):
        pass
