from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.services.PendingExpensesService import PendingExpensesService

from src.widgets.BaseWidget import BaseWidget
from src.widgets.ComboBox import ComboBox

from src.misc.DateConverter import DateConverter

from globals import widgets_pool as wpool

class DateFilter(QWidget, BaseWidget):
    def __init__(self, *args, **kwargs):
        super(DateFilter, self).__init__(*args, **kwargs)

        self.expenses_service = PendingExpensesService()
        self.cboxes = {}

        date_categories = [
            'day_from', 'month_from', 'year_from',
            'day_to', 'month_to', 'year_to'
        ]

        for dc in date_categories:
            self.add_cbox(dc)
            self.cbox(dc).currentIndexChanged.connect(self.date_changed)

    def get_widgets_from_pool(self):
        pass

    def create_layout(self):
        layout = QVBoxLayout()

        from_layout = self.create_date_layout('from')
        to_layout = self.create_date_layout('to')

        inner_layout = QVBoxLayout()
        inner_layout.addLayout(from_layout)
        inner_layout.addLayout(to_layout)

        group_box = QGroupBox("Fechas")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.setLayout(layout)

    def init_widgets(self):
        self.update_top_dates()

    def set_visibility_days(self, visibility):
        self.cbox('day_from').setVisible(visibility)
        self.cbox('day_to').setVisible(visibility)

    def create_date_layout(self, cbx_type):
        title = 'Desde' if cbx_type == 'from' else 'Hasta'

        layout = QHBoxLayout()

        layout.addWidget(QLabel(title + ':'))
        layout.addWidget(self.cbox(f'day_{cbx_type}'))
        layout.addWidget(self.cbox(f'month_{cbx_type}'))
        layout.addWidget(self.cbox(f'year_{cbx_type}'))

        return layout

    def date_changed(self, index):
        day_from = self.cbox('day_from').currentIndex() + 1
        month_from = self.cbox('month_from').currentIndex() + 1
        year_from = self.cbox('year_from').currentText()

        day_to = self.cbox('day_to').currentIndex() + 1
        month_to = self.cbox('month_to').currentIndex() + 1
        year_to = self.cbox('year_to').currentText()

        dates = {
            'from': DateConverter().format_raw_dmy(day_from, month_from, year_from),
            'to': DateConverter().format_raw_dmy(day_to, month_to, year_to)
        }

        wpool.execute('filter-widget', 'change_dates', dates)

    def update_top_dates(self):
        expenses = self.expenses_service.get_expenses()
        dates = list(map(lambda x: x['date'], expenses))

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
        year_index = int(self.cbox(f'year_{combo_group}').findText(year))

        self.cbox(f'day_{combo_group}').setCurrentIndex(day_index)
        self.cbox(f'month_{combo_group}').setCurrentIndex(month_index)
        self.cbox(f'year_{combo_group}').setCurrentIndex(year_index)

    def add_cbox(self, combo_name_raw):
        combo_name_split = combo_name_raw.split('_')
        combo_group = combo_name_split[1]
        combo_name = combo_name_split[0]

        if not combo_group in self.cboxes:
            self.cboxes[combo_group] = {}

        self.cboxes[combo_group][combo_name] = self.create_combobox(f'get_{combo_name}s')

    def cbox(self, combo_name_raw):
        combo_name_split = combo_name_raw.split('_')
        combo_group = combo_name_split[1]
        combo_name = combo_name_split[0]

        return self.cboxes[combo_group][combo_name]
