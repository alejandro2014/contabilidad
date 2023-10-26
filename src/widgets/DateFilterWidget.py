from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.dialogs.WidgetCreator import WidgetCreator

from src.events.ListenerNode import ListenerNode

from src.services.ComboBoxService import ComboBoxService
from src.services.PendingExpensesService import PendingExpensesService

from src.model.date_filter import DateFilter

from DateConverter import DateConverter

class DateFilterWidget(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(DateFilterWidget, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'date-filter', listeners_pool)

        self.__combobox_service = ComboBoxService()

        widget_creator = WidgetCreator(self.__combobox_service)

        
        self.expenses_service = PendingExpensesService()

        self.date_filter = DateFilter()

        self.cbx = {
            'from': {
                'day': widget_creator.create_combobox('day'),
                'month': widget_creator.create_combobox('month'),
                'year': widget_creator.create_combobox('year')
            },
            'to': {
                'day': widget_creator.create_combobox('day'),
                'month': widget_creator.create_combobox('month'),
                'year': widget_creator.create_combobox('year')
            }
        }

        layout = QVBoxLayout()
        self.setLayout(layout)

        from_layout = self.create_date_layout('Desde', self.cbx['from'])
        to_layout = self.create_date_layout('Hasta', self.cbx['to'])

        inner_layout = QVBoxLayout()
        inner_layout.addLayout(from_layout)
        inner_layout.addLayout(to_layout)

        group_box = QGroupBox("Fechas")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.cbx['from']['day'].currentIndexChanged.connect(self.date_changed)
        self.cbx['from']['month'].currentIndexChanged.connect(self.date_changed)
        self.cbx['from']['year'].currentIndexChanged.connect(self.date_changed)
        self.cbx['to']['day'].currentIndexChanged.connect(self.date_changed)
        self.cbx['to']['month'].currentIndexChanged.connect(self.date_changed)
        self.cbx['to']['year'].currentIndexChanged.connect(self.date_changed)

        self.update_top_dates()

    def create_date_layout(self, title, cbx):
        layout = QHBoxLayout()

        layout.addWidget(QLabel(title + ':'))
        layout.addWidget(cbx['day'])
        layout.addWidget(cbx['month'])
        layout.addWidget(cbx['year'])

        return layout

    def date_changed(self, index):
        day_from = self.cbx['from']['day'].currentIndex() + 1
        month_from = self.cbx['from']['month'].currentIndex() + 1
        year_from = self.cbx['from']['year'].currentText()

        day_to = self.cbx['to']['day'].currentIndex() + 1
        month_to = self.cbx['to']['month'].currentIndex() + 1
        year_to = self.cbx['to']['year'].currentText()

        dates = {
            'from': DateConverter().format_raw_dmy(day_from, month_from, year_from),
            'to': DateConverter().format_raw_dmy(day_to, month_to, year_to)
        }

        self.send_event('filter-widget', 'change_dates', dates)

    def update_top_dates(self):
        expenses = self.expenses_service.get_expenses()
        dates = [ x['date'] for x in expenses ]

        top_dates = self.get_top_dates(dates)

        if top_dates != None:
            self.change_filter_dates(top_dates['from'], top_dates['to'])

    def get_top_dates(self, dates):
        min_date = None
        max_date = None

        for date in dates:
            if max_date == None or date > max_date:
                max_date = date

            if min_date == None or date < min_date:
                min_date = date

        if min_date == None or max_date == None:
            return None

        return {
            'from': min_date,
            'to': max_date
        }

    def change_filter_dates(self, date_from, date_to):
        if date_from == None or date_to == None:
            return

        self.change_filter_date('from', date_from)
        self.change_filter_date('to', date_to)

    def change_filter_date(self, combo_group, date_value):
        day = date_value[6:8]
        month = date_value[4:6]
        year = date_value[0:4]

        day_index = int(day) - 1
        month_index = int(month) - 1
        year_index = int(self.cbx[combo_group]['year'].findText(year))

        self.cbx[combo_group]['day'].setCurrentIndex(day_index)
        self.cbx[combo_group]['month'].setCurrentIndex(month_index)
        self.cbx[combo_group]['year'].setCurrentIndex(year_index)
