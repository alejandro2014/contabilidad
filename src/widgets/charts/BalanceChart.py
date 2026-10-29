from PySide6 import QtCharts
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QCursor, QFont, QPainter, QPen
from PySide6.QtWidgets import QToolTip

from src.services.ChartService import ChartService

from src.widgets.charts.ChartPalette import ChartPalette

class BalanceChart(QtCharts.QChartView):
    TITLE = 'Saldo de la cuenta a final de mes (€)'

    def __init__(self):
        super(BalanceChart, self).__init__()

        self.chart_palette = ChartPalette()
        self.chart_info = None

        self.chart_service = ChartService()

        self.setRenderHint(QPainter.Antialiasing)

    def reload(self, filter):
        chart_info = self.chart_service.get_balance_chart_info(filter)
        self.chart_info = chart_info

        chart = QtCharts.QChart()
        self.chart_palette.apply_theme(chart)
        chart.legend().hide()

        known = [ balance for balance in chart_info['balances'] if balance is not None ]

        # The statements loaded before the balance was stored don't have it
        if len(known) == 0:
            chart.setTitle(f'{self.TITLE}<br>Sin saldos: vuelve a cargar los extractos para verlo')
        else:
            last = known[-1]
            chart.setTitle(f'{self.TITLE}: {self.chart_palette.format_amount(last)}')

        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append(chart_info['short_months'])
        axis_x.setLabelsAngle(0 if len(chart_info['months']) < 9 else 90)
        axis_x.setLabelsFont(QFont('Monospace', 11))
        axis_x.setGridLineVisible(False)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        axis_y = QtCharts.QValueAxis()
        axis_y.setLabelFormat('%.0f')
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        series = self.create_series(chart_info['balances'])
        chart.addSeries(series)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        # From zero, so the changes don't look bigger than they are (below it when the account is overdrawn)
        low, high = (min(known), max(known)) if len(known) > 0 else (0, 1)
        axis_y.setRange(min(low, 0), high if high > low else low + 1)
        axis_y.applyNiceNumbers()

        self.setChart(chart)

        return chart_info

    def create_series(self, balances):
        series = QtCharts.QLineSeries()

        # The months before the first balance known are left out
        for index, balance in enumerate(balances):
            if balance is not None:
                series.append(QPointF(index, balance))

        series.setPen(QPen(QColor(ChartPalette.SERIES[0]), 2))
        series.setPointsVisible(True)
        series.setMarkerSize(4)
        series.hovered.connect(self.point_hovered)

        return series

    def point_hovered(self, point, state):
        if not state:
            QToolTip.hideText()
            return

        index = round(point.x())
        month = self.chart_info['months'][index]

        QToolTip.showText(QCursor.pos(), f'{month}\n{self.chart_palette.format_amount(self.chart_info["balances"][index])}')
