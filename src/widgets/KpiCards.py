from PySide6 import QtCore
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.widgets.charts.ChartPalette import ChartPalette

class KpiCard(QFrame):
    def __init__(self, title, *args, **kwargs):
        super(KpiCard, self).__init__(*args, **kwargs)

        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.title = self.create_label(title, 10)
        self.value = self.create_label('', 16, True)
        self.detail = self.create_label('', 10)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(2)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.value)
        self.layout.addWidget(self.detail)
        self.setLayout(self.layout)

    def add_button(self, text):
        button = QPushButton(text)
        self.layout.addWidget(button, 0, QtCore.Qt.AlignHCenter)

        return button

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
    COLUMNS_NO = 4

    # Text after the change of each figure, for each period they can be compared with
    COMPARISON_TEXTS = { 'previous': 'vs. periodo anterior', 'last_year': 'vs. mismo periodo del año pasado' }

    def __init__(self, *args, **kwargs):
        super(KpiCards, self).__init__(*args, **kwargs)

        self.chart_palette = ChartPalette()

        self.cards = {
            'expenses': KpiCard('Gastos'),
            'incomes': KpiCard('Ingresos'),
            'balance': KpiCard('Ahorro'),
            'savings_rate': KpiCard('Tasa de ahorro'),
            'monthly_average': KpiCard('Gasto medio mensual'),
            'top_category': KpiCard('Categoría con más gasto'),
            'max_month': KpiCard('Mes con más gasto'),
            'pending': KpiCard('Pendientes de clasificar')
        }

        # Opens the screen to classify them, only shown when there are pending expenses
        self.pending_button = self.cards['pending'].add_button('Clasificar')
        self.pending_button.setCursor(QtCore.Qt.PointingHandCursor)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        for i, card in enumerate(self.cards.values()):
            layout.addWidget(card, i // self.COLUMNS_NO, i % self.COLUMNS_NO)

        for column in range(self.COLUMNS_NO):
            layout.setColumnStretch(column, 1)

        self.setLayout(layout)

    def reload(self, kpis, comparison=None):
        amount = self.chart_palette.format_amount
        # Without a period to compare with, the cards explain what they show
        changes = kpis.get('changes') if comparison is not None else None

        self.cards['expenses'].set_value(amount(kpis['expenses']), self.change_text(changes, 'expenses', comparison))
        self.cards['incomes'].set_value(amount(kpis['incomes']), self.change_text(changes, 'incomes', comparison))

        balance = kpis['balance']
        balance_detail = 'Ingresos - gastos' if changes is None else self.change_text(changes, 'balance', comparison)
        self.cards['balance'].set_value(self.signed(amount(balance), balance), balance_detail, self.status_color(balance))

        rate = kpis['savings_rate']
        if rate is None:
            self.cards['savings_rate'].set_value('-', 'Sin ingresos')
        else:
            rate_detail = 'de los ingresos' if changes is None else self.change_text(changes, 'savings_rate', comparison)
            self.cards['savings_rate'].set_value(self.signed(f'{rate}%', rate), rate_detail, self.status_color(rate))

        self.cards['monthly_average'].set_value(amount(kpis['monthly_average']), self.change_text(changes, 'monthly_average', comparison))

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
        self.pending_button.setVisible(pending > 0)

    def change_text(self, changes, kpi, comparison):
        if changes is None:
            return ''

        change = changes[kpi]

        # Nothing to compare with when the other period has no data
        if change is None:
            return 'Sin datos para comparar'

        if kpi == 'balance':
            text = self.signed(self.chart_palette.format_amount(change), change)
        elif kpi == 'savings_rate':
            text = self.signed(f'{change:.1f}'.replace('.', ',') + ' pp', change)
        else:
            text = f'{round(change):+d} %'

        return f'{text} {self.COMPARISON_TEXTS[comparison]}'

    def signed(self, text, value):
        return f'+{text}' if value > 0 else text

    def status_color(self, value):
        return ChartPalette.GOOD if value >= 0 else ChartPalette.CRITICAL
