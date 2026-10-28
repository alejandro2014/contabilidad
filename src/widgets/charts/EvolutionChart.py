from PySide6 import QtCharts
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QCursor, QFont, QPainter, QPen
from PySide6.QtWidgets import QToolTip

from src.services.ChartService import ChartService

from src.widgets.charts.ChartPalette import ChartPalette

class EvolutionChart(QtCharts.QChartView):
    CATEGORIES_NO = 5

    def __init__(self):
        super(EvolutionChart, self).__init__()

        self.title = f'Evolución de las {self.CATEGORIES_NO} categorías con más gasto (€)'
        self.chart_palette = ChartPalette()
        self.chart_info = None

        self.chart_service = ChartService()

        self.setRenderHint(QPainter.Antialiasing)

    def reload(self, filter, colors):
        # The colors of the pie chart are sorted by amount, and "Otros" is not a real category
        top_categories = [ c for c in colors if c != ChartPalette.OTHERS_NAME ][:self.CATEGORIES_NO]

        chart_info = self.chart_service.get_evolution_chart_info(filter, top_categories)
        self.chart_info = chart_info

        chart = QtCharts.QChart()
        chart.setTitle(self.title)

        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append(chart_info['short_months'])
        axis_x.setLabelsAngle(0 if len(chart_info['months']) < 9 else 90)
        axis_x.setLabelsFont(QFont('Monospace', 11))
        axis_x.setGridLineVisible(False)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        axis_y = QtCharts.QValueAxis()
        axis_y.setLabelFormat('%.0f')
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        max_amount = 0.0

        for category, amounts in chart_info['series'].items():
            series = self.create_series(category, amounts, colors[category])
            chart.addSeries(series)
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

            max_amount = max([ max_amount ] + amounts)

        axis_y.setRange(0, max_amount if max_amount > 0 else 1)
        axis_y.applyNiceNumbers()

        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.setChart(chart)

        return chart_info

    def create_series(self, category, amounts, color):
        series = QtCharts.QLineSeries()
        series.setName(category)

        for index, amount in enumerate(amounts):
            series.append(QPointF(index, amount))

        series.setPen(QPen(color, 2))
        series.setPointsVisible(True)
        series.setMarkerSize(4)
        series.hovered.connect(lambda point, state: self.point_hovered(category, point, state))

        return series

    def point_hovered(self, category, point, state):
        if not state:
            QToolTip.hideText()
            return

        index = round(point.x())
        month = self.chart_info['months'][index]
        amount = self.chart_info['series'][category][index]

        QToolTip.showText(QCursor.pos(), f'{month}\n{category}: {self.chart_palette.format_amount(amount)}')
