from PySide6 import QtCore
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from src.widgets.charts.ChartPalette import ChartPalette

class KpiCard(QFrame):
    def __init__(self, title, *args, **kwargs):
        super(KpiCard, self).__init__(*args, **kwargs)

        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.title = self.create_label(title, 10)
        self.value = self.create_label('', 16, True)
        self.detail = self.create_label('', 10)

        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.detail)
        self.setLayout(layout)

    def set_value(self, value, detail='', color=None):
        self.value.setText(value)
        self.detail.setText(detail)
        # The color only highlights the value, the sign or the text tells if it is good or bad
        self.value.setStyleSheet('' if color is None else f'color: {color}')

    def create_label(self, text, font_size, bold=False):
        font = QFont()
        font.setPointSize(font_size)
        font.setBold(bold)

        label = QLabel(text)
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        return label

class KpiCards(QWidget):
    COLUMNS_NO = 7

    def __init__(self, *args, **kwargs):
        super(KpiCards, self).__init__(*args, **kwargs)

        self.chart_palette = ChartPalette()

        self.cards = {
            'incomes': KpiCard('Ingresos'),
            'balance': KpiCard('Ahorro'),
            'savings_rate': KpiCard('Tasa de ahorro'),
            'monthly_average': KpiCard('Gasto medio mensual'),
            'top_category': KpiCard('Categoría con más gasto'),
            'max_month': KpiCard('Mes con más gasto'),
            'pending': KpiCard('Pendientes de clasificar')
        }

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        for i, card in enumerate(self.cards.values()):
            layout.addWidget(card, i // self.COLUMNS_NO, i % self.COLUMNS_NO)

        for column in range(self.COLUMNS_NO):
            layout.setColumnStretch(column, 1)

        self.setLayout(layout)

    def reload(self, kpis):
        amount = self.chart_palette.format_amount

        self.cards['incomes'].set_value(amount(kpis['incomes']))

        balance = kpis['balance']
        self.cards['balance'].set_value(self.signed(amount(balance), balance), 'Ingresos - gastos', self.status_color(balance))

        rate = kpis['savings_rate']
        if rate is None:
            self.cards['savings_rate'].set_value('-', 'Sin ingresos')
        else:
            self.cards['savings_rate'].set_value(self.signed(f'{rate}%', rate), 'de los ingresos', self.status_color(rate))

        self.cards['monthly_average'].set_value(amount(kpis['monthly_average']))

        top_category = kpis['top_category']
        if top_category is None:
            self.cards['top_category'].set_value('-')
        else:
            self.cards['top_category'].set_value(top_category['name'], amount(top_category['amount']))

        max_month = kpis['max_month']
        if max_month is None:
            self.cards['max_month'].set_value('-')
        else:
            self.cards['max_month'].set_value(max_month['name'], amount(max_month['amount']))

        # The figures are not complete while there are expenses to classify
        pending = kpis['pending']
        self.cards['pending'].set_value(str(pending), 'En el periodo, faltan datos' if pending > 0 else 'Todo clasificado', ChartPalette.WARNING if pending > 0 else None)

    def signed(self, text, value):
        return f'+{text}' if value > 0 else text

    def status_color(self, value):
        return ChartPalette.GOOD if value >= 0 else ChartPalette.CRITICAL
