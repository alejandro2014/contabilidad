from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from DateConverter import DateConverter

from src.events.ListenerNode import ListenerNode
from src.model.date_filter import DateFilter
from src.services.expenses_service import ExpensesService
from src.services.combobox_services.days_service import DaysService
from src.services.combobox_services.months_service import MonthsService
from src.services.combobox_services.years_service import YearsService
from src.gui.widgets.combobox import ComboBox

from src.gui.widgets.date_selector import DateSelector


class DateFilterWidget(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(DateFilterWidget, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'date-filter', listeners_pool)
        
        #self.expenses_service = PendingExpensesService()
        self.expenses_service = ExpensesService()

        self.date_filter = DateFilter()

        self.cbx = {
            'from': {
                'day': ComboBox('Día', DaysService()),
                'month': ComboBox('Mes', MonthsService()),
                'year': ComboBox('Año', YearsService())
            },
            'to': {
                'day': ComboBox('Día', DaysService()),
                'month': ComboBox('Mes', MonthsService()),
                'year': ComboBox('Año', YearsService())
            }
        }

        layout = QVBoxLayout()
        self.setLayout(layout)

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(DateSelector('Desde'))
        inner_layout.addWidget(DateSelector('Hasta'))

        group_box = QGroupBox("Fechas")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        """
        self.cbx['from']['day'].currentIndexChanged.connect(self.date_changed)
        self.cbx['from']['month'].currentIndexChanged.connect(self.date_changed)
        self.cbx['from']['year'].currentIndexChanged.connect(self.date_changed)
        self.cbx['to']['day'].currentIndexChanged.connect(self.date_changed)
        self.cbx['to']['month'].currentIndexChanged.connect(self.date_changed)
        self.cbx['to']['year'].currentIndexChanged.connect(self.date_changed)
        """

        #self.update_top_dates()

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
        date_from, date_to = TopDateGetter().get_top_dates('pending')

        self.change_filter_dates(date_from, date_to)

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

class TopDateGetter:
    def __init__(self):
        self.expenses_service = ExpensesService()
        
    def get_top_dates(self, expenses_type):
        if expenses_type == 'pending':
            expenses = self.expenses_service.get_pending_expenses()
        else:
            expenses = self.expenses_service.get_classified_expenses()

        dates = [ e.date for e in expenses ]

        if len(dates) == 0:
            return None, None
        
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