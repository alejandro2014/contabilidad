from PySide6 import QtCharts
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QCursor, QFont, QPainter, QPen
from PySide6.QtWidgets import QToolTip

from src.services.ChartService import ChartService

from src.widgets.charts.ChartPalette import ChartPalette

class SavingsChart(QtCharts.QChartView):
    TITLE = 'Ahorro por mes (€)'

    # Clicking a bar opens the movements to the savings account of its month, with this filter
    open_expenses = Signal(dict)

    def __init__(self):
        super(SavingsChart, self).__init__()

        self.chart_palette = ChartPalette()
        self.chart_info = None
        self.filter = None

        self.chart_service = ChartService()

        self.setRenderHint(QPainter.Antialiasing)

    def reload(self, filter):
        chart_info = self.chart_service.get_savings_chart_info(filter)
        self.chart_info = chart_info
        self.filter = filter

        chart = QtCharts.QChart()
        self.chart_palette.apply_theme(chart)
        chart.setTitle(self.get_title(chart_info))

        # What is sent to savings goes up and what comes back goes down, in the same bar of the month
        bar_series = QtCharts.QStackedBarSeries()
        bar_series.append(self.create_bar_set('Aportado', chart_info['deposits'], ChartPalette.INCOME))
        bar_series.append(self.create_bar_set('Retirado', chart_info['withdrawals'], ChartPalette.EXPENSE))
        chart.addSeries(bar_series)

        line_series = self.create_accumulated_series(chart_info['accumulated'])
        chart.addSeries(line_series)

        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append(chart_info['short_months'])
        axis_x.setLabelsAngle(0 if len(chart_info['months']) < 9 else 90)
        axis_x.setLabelsFont(QFont('Monospace', 11))
        axis_x.setGridLineVisible(False)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        axis_y = QtCharts.QValueAxis()
        axis_y.setLabelFormat('%.0f')
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        for series in [ bar_series, line_series ]:
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

        # From zero, and below it when more has been taken out than put in
        values = chart_info['deposits'] + chart_info['withdrawals'] + chart_info['accumulated']
        low, high = min(values + [ 0.0 ]), max(values + [ 0.0 ])
        axis_y.setRange(low, high if high > low else low + 1)
        axis_y.applyNiceNumbers()

        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.setChart(chart)

        return chart_info

    def get_title(self, chart_info):
        if len(chart_info['categories']) == 0:
            return f'{self.TITLE}<br>Marca un tipo como «Ahorro» en Configuración > Tipos de gastos'

        return f"{self.TITLE}: {self.chart_palette.format_amount(chart_info['total'])}"

    def create_bar_set(self, name, amounts, color):
        bar_set = QtCharts.QBarSet(name)
        bar_set.setColor(QColor(color))
        bar_set.setBorderColor(QColor(color))
        bar_set.append(amounts)
        bar_set.hovered.connect(self.bar_hovered)
        bar_set.clicked.connect(self.bar_clicked)

        return bar_set

    def create_accumulated_series(self, accumulated):
        series = QtCharts.QLineSeries()
        series.setName('Acumulado')

        for index, total in enumerate(accumulated):
            series.append(QPointF(index, total))

        series.setPen(QPen(QColor(ChartPalette.SERIES[0]), 2))
        series.setPointsVisible(True)
        series.setMarkerSize(4)
        series.hovered.connect(lambda point, state: self.bar_hovered(state, round(point.x())))

        return series

    def bar_clicked(self, index):
        # With a single savings type its movements are the ones shown, with several the whole month
        categories = self.chart_info['categories']
        category = categories[0] if len(categories) == 1 else None

        self.open_expenses.emit(self.chart_service.expenses_filter(self.filter, self.chart_info['year_months'][index], category))

    def bar_hovered(self, status, index):
        if not status:
            QToolTip.hideText()
            self.unsetCursor()
            return

        self.setCursor(Qt.PointingHandCursor)

        info = self.chart_info
        format_amount = self.chart_palette.format_amount
        lines = [
            info['months'][index],
            f"Aportado: {format_amount(info['deposits'][index])}",
            f"Retirado: {format_amount(-info['withdrawals'][index])}",
            f"Neto del mes: {format_amount(info['amounts'][index])}",
            f"Acumulado: {format_amount(info['accumulated'][index])}",
            'Clic para ver los movimientos'
        ]

        QToolTip.showText(QCursor.pos(), '\n'.join(lines))
