from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from src.widgets.Classifier import Classifier
from src.widgets.DateFilter import DateFilter
from src.widgets.TextFilter import TextFilter
from src.widgets.SecondaryFilters import SecondaryFilters

from src.widgets.RootWidget import RootWidget

from globals import widgets_pool as wpool

class FilterWidget(RootWidget):
    def __init__(self, screen_type):
        super().__init__()

        self.table_name = screen_type + '-expenses-table'
        self.widget_ids = ['date-filter', 'text-filter', 'sum-text', 'secondary-filters', 'classifier']

        self.filter = {
            'date': {
                'from': None,
                'to': None
            },
            'search_value': None
        }

    def create_layout(self):
        column1 = QVBoxLayout()
        column1.addWidget(self.date_filter)
        column1.addWidget(self.text_filter)

        column2 = QVBoxLayout()
        column2.addWidget(self.classifier)

        column3 = QVBoxLayout()
        column3.addWidget(self.sum_text)

        main_part = QHBoxLayout()

        main_part.addLayout(column1)
        main_part.addLayout(column2)
        main_part.addLayout(column3)

        main_layout = QVBoxLayout()
        main_layout.addLayout(main_part)

        secondary_part = QHBoxLayout()
        secondary_part.addWidget(self.secondary_filters)

        main_layout.addLayout(secondary_part)

        self.setLayout(main_layout)

    def set_visibility_pending(self):
        if hasattr(self, 'classifier'):
            self.classifier.setVisible(True)

        if hasattr(self, 'text_filter'):
            self.text_filter.setVisible(True)

        if hasattr(self, 'secondary_filters'):
            self.secondary_filters.setVisible(True)

        wpool.execute('secondary-filters', 'set_visibility_group_by_type', False)
        wpool.execute('date-filter', 'set_visibility_days', True)

    def set_visibility_classified(self):
        if hasattr(self, 'classifier'):
            self.classifier.setVisible(False)

        if hasattr(self, 'text_filter'):
            self.text_filter.setVisible(True)

        if hasattr(self, 'secondary_filters'):
            self.secondary_filters.setVisible(True)

        wpool.execute('secondary-filters', 'set_visibility_group_by_type', True)
        wpool.execute('date-filter', 'set_visibility_days', True)

    def set_visibility_charts(self):
        if hasattr(self, 'classifier'):
            self.classifier.setVisible(False)

        if hasattr(self, 'text_filter'):
            self.text_filter.setVisible(False)

        if hasattr(self, 'secondary_filters'):
            self.secondary_filters.setVisible(False)

        wpool.execute('sum-text', 'hide_records_no')
        wpool.execute('date-filter', 'set_visibility_days', False)

    def change_dates(self, dates):
        self.filter['date']['from'] = dates['from']
        self.filter['date']['to'] = dates['to']

        wpool.execute(self.table_name, 'refresh', self.filter)
        wpool.execute('view-charts-screen', 'reload_charts')

    def change_search_value(self, search_value):
        self.filter['search_value'] = search_value

        wpool.execute(self.table_name, 'refresh', self.filter)
