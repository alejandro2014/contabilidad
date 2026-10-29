from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from src.dialogs.WidgetCreator import WidgetCreator
from src.events.ListenerNode import ListenerNode

from src.widgets.Classifier import Classifier
from src.widgets.DateFilterWidget import DateFilterWidget
from src.widgets.SearchFilter import SearchFilter
from src.widgets.Summatory import Summatory
from src.widgets.SecondaryFilters import SecondaryFilters

class FilterWidget(QWidget, ListenerNode):
    def __init__(self, screen_type, listeners_pool, *args, **kwargs):
        super(FilterWidget, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'filter-widget', listeners_pool)

        self.screen_type = screen_type
        self.table_name = screen_type + '-expenses-table'

        self.filter = {
            'date': {
                'from': None,
                'to': None
            },
            'search_value': None,
            'amount': {
                'from': None,
                'to': None
            },
            'category': None,
            'tag': None
        }

        self.date_filter = DateFilterWidget(listeners_pool)
        self.search_filter = SearchFilter(listeners_pool, screen_type == 'classified')
        self.summatory = Summatory(listeners_pool)
        self.secondary_filters = SecondaryFilters(listeners_pool)

        show_classify_button = screen_type == 'pending'
        self.classifier = Classifier(listeners_pool, show_classify_button)

        column1 = QVBoxLayout()
        column1.addWidget(self.date_filter)

        if screen_type != 'chart':
            column1.addWidget(self.search_filter)

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

            if screen_type == 'classified':
                widget_creator = WidgetCreator()

                self.unclassify_button = widget_creator.create_button('Desclasificar seleccionados', 'cancel', self.unclassify_selected)
                self.notes_button = widget_creator.create_button('Notas y etiquetas', 'ok', self.edit_notes_selected)
                self.export_button = widget_creator.create_button('Exportar', 'upload', lambda: self.send_event('view-expenses-screen', 'export_table'))

                buttons = QVBoxLayout()
                buttons.addWidget(self.notes_button)
                buttons.addWidget(self.unclassify_button)
                buttons.addWidget(self.export_button)
                secondary_part.addLayout(buttons)

            main_layout.addLayout(secondary_part)

        self.setLayout(main_layout)

    def change_dates(self, dates):
        self.filter['date']['from'] = dates['from']
        self.filter['date']['to'] = dates['to']

        if self.screen_type == 'chart':
            self.send_event('view-charts-screen', 'reload_charts', self.filter)
        else:
            self.send_event(self.table_name, 'refresh_rows', self.filter)

    def unclassify_selected(self):
        self.send_event(self.table_name, 'unclassify_selected')
        self.send_event('status-bar', 'refresh')

    def edit_notes_selected(self):
        self.send_event(self.table_name, 'edit_notes_selected')

    def change_search(self, search):
        self.update_search(search)

        self.send_event(self.table_name, 'refresh_rows', self.filter)

    def update_search(self, search):
        self.filter['search_value'] = search['search_value']
        self.filter['amount']['from'] = search['amount']['from']
        self.filter['amount']['to'] = search['amount']['to']
        self.filter['category'] = search['category']
        self.filter['tag'] = search['tag']

    def set_filter(self, filter):
        # A filter chosen somewhere else (a chart of the dashboard), shown in the widgets. The dates are not kept
        # as the last range chosen
        self.search_filter.set_search(filter.get('search_value'), filter.get('category'), filter.get('tag'))
        self.update_search(self.search_filter.get_search())

        self.date_filter.change_filter_dates(filter['date']['from'], filter['date']['to'], remember=False)
