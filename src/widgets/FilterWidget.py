from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

from src.widgets.Classifier import Classifier
from src.widgets.DateFilter import DateFilter
from src.widgets.TextFilter import TextFilter
from src.widgets.Summatory import Summatory
from src.widgets.SecondaryFilters import SecondaryFilters

class FilterWidget(QWidget, ListenerNode):
    def __init__(self, screen_type, listeners_pool, *args, **kwargs):
        super(FilterWidget, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'filter-widget', listeners_pool)

        self.table_name = screen_type + '-expenses-table'

        self.filter = {
            'date': {
                'from': None,
                'to': None
            },
            'search_value': None
        }

        self.date_filter = DateFilter(listeners_pool)
        self.text_filter = TextFilter(listeners_pool)
        self.summatory = Summatory(listeners_pool)
        self.secondary_filters = SecondaryFilters(listeners_pool)

        show_classify_button = screen_type == 'pending'
        self.classifier = Classifier(listeners_pool, show_classify_button)

        column1 = QVBoxLayout()
        column1.addWidget(self.date_filter)

        if screen_type != 'chart':
            column1.addWidget(self.text_filter)

            if screen_type == 'pending':
                column2 = QVBoxLayout()
                column2.addWidget(self.classifier)

        column3 = QVBoxLayout()
        column3.addWidget(self.summatory)

        main_part = QHBoxLayout()
        main_part.addLayout(column1)

        if screen_type == 'pending':
            main_part.addLayout(column2)

        main_part.addLayout(column3)

        main_layout = QVBoxLayout()
        main_layout.addLayout(main_part)

        if screen_type != 'chart':
            secondary_part = QHBoxLayout()
            secondary_part.addWidget(self.secondary_filters)

            main_layout.addLayout(secondary_part)

        self.setLayout(main_layout)

    def change_dates(self, dates):
        self.filter['date']['from'] = dates['from']
        self.filter['date']['to'] = dates['to']

        self.send_event(self.table_name, 'refresh_rows', self.filter)
        self.send_event('view-charts-screen', 'reload_charts', self.filter)

    def change_search_value(self, search_value):
        self.filter['search_value'] = search_value

        self.send_event(self.table_name, 'refresh_rows', self.filter)
