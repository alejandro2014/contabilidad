import datetime

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from DateConverter import DateConverter

from src.dialogs.WidgetCreator import WidgetCreator
from src.events.ListenerNode import ListenerNode
from src.model.date_filter import DateFilter
from src.services.expenses_service import ExpensesService

class DateFilterWidget(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(DateFilterWidget, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'date-filter', listeners_pool)

        widget_creator = WidgetCreator()
        
        #self.expenses_service = PendingExpensesService()
        self.expenses_service = ExpensesService()

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
        inner_layout.addLayout(self.create_periods_layout())

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

    def create_periods_layout(self):
        layout = QHBoxLayout()

        for title, period in [ ('Este mes', 'this_month'), ('Mes pasado', 'last_month'), ('Últimos 3 meses', 'last_3_months'),
                               ('Últimos 12 meses', 'last_12_months'), ('Este año', 'this_year'), ('Año pasado', 'last_year') ]:
            button = QPushButton(title)
            button.clicked.connect(lambda checked=False, period=period: self.select_period(period))
            layout.addWidget(button)

        return layout

    def select_period(self, period):
        date_from, date_to = self.get_period_dates(period, datetime.date.today())

        self.change_filter_dates(date_from.strftime('%Y%m%d'), date_to.strftime('%Y%m%d'))

    def get_period_dates(self, period, today):
        if period == 'this_month':
            return today.replace(day=1), today

        if period == 'last_month':
            last_day = today.replace(day=1) - datetime.timedelta(days=1)
            return last_day.replace(day=1), last_day

        if period in [ 'last_3_months', 'last_12_months' ]:
            # The current month is one of them
            months_back = 2 if period == 'last_3_months' else 11
            month_index = today.year * 12 + today.month - 1 - months_back
            return datetime.date(month_index // 12, month_index % 12 + 1, 1), today

        if period == 'this_year':
            return datetime.date(today.year, 1, 1), today

        if period == 'last_year':
            return datetime.date(today.year - 1, 1, 1), datetime.date(today.year - 1, 12, 31)

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
        today = datetime.date.today()
        date_from = f'{today.year}0101'
        date_to = today.strftime('%Y%m%d')

        self.change_filter_dates(date_from, date_to)

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

        return min_date, max_date

    def change_filter_dates(self, date_from, date_to):
        if date_from == None or date_to == None:
            return

        combos = list(self.cbx['from'].values()) + list(self.cbx['to'].values())

        # Every combo would send its own change, so the screen is reloaded only once at the end
        for combo in combos:
            combo.blockSignals(True)

        self.change_filter_date('from', date_from)
        self.change_filter_date('to', date_to)

        for combo in combos:
            combo.blockSignals(False)

        self.date_changed(None)

    def change_filter_date(self, combo_group, date_value):
        day = date_value[6:8]
        month = date_value[4:6]
        year = date_value[0:4]

        day_index = int(day) - 1
        month_index = int(month) - 1
        # The years before the first one of the combo are not available
        year_index = max(int(self.cbx[combo_group]['year'].findText(year)), 0)

        self.cbx[combo_group]['day'].setCurrentIndex(day_index)
        self.cbx[combo_group]['month'].setCurrentIndex(month_index)
        self.cbx[combo_group]['year'].setCurrentIndex(year_index)
