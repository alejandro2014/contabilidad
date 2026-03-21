from PySide2 import QtCore

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Qt
from PySide2.QtGui import QPainter, QPen, QColor

from src.services.ChartService import ChartService

from globals import widgets_pool as wpool

class PieChart(QtCharts.QChartView):
    def __init__(self):
        super().__init__()

        self.chart_service = ChartService()
        self.series = None

        self.setRenderHint(QPainter.Antialiasing)

    def get_widgets_from_pool(self):
        pass

    def create_layout(self):
        pass

    def init_widgets(self):
        pass

    def reload(self, filter):
        chart_info = self.chart_service.get_pie_chart_info(filter)

        if chart_info == {}:
            return

        wpool.execute('sum-text', 'update_expenses_sum_from_chart', chart_info)

        chart = self.chart()

        if self.series:
            chart.removeSeries(self.series)

        self.series = self.compose_series(chart_info)

        if self.series:
            chart.addSeries(self.series)

        chart.setTitle('Gastos relativos')

        chart.legend().setAlignment(Qt.AlignRight)

    def compose_series(self, categories):
        if not categories:
            return None

        series = QtCharts.QPieSeries()
        colors = self.get_colors(categories)
        total = sum(categories.values())

        for i, category_name in enumerate(categories):
            amount = categories[category_name]
            title = self.get_chart_slice_title(categories, category_name, amount, total)
            series.append(title, amount)

            slice = series.slices()[i]
            slice.setBrush(colors[i])

        return series

    def get_chart_slice_title(self, categories, category_name, amount, total):
        percentage = round(amount / total * 100.0, 2)

        return category_name + ' (' + str(percentage) + '%) - ' + str(amount) + '€'

    def get_colors(self, categories):
        color_palette = [
            QColor(200, 0, 0), QColor(0, 0, 200), QColor(0, 200, 0), QColor(200, 200, 0),
            QColor(150, 40, 80),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),

            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),

            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),

            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),

            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),

            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),

            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),

            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),

            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200)),
            QColor(self.random(200), self.random(200), self.random(200))
        ]

        colors = []

        for i, category in enumerate(categories):
            color = color_palette[i]
            colors.append(color)

        return colors

    def random(self, boundary):
        return QtCore.QRandomGenerator.global_().bounded(boundary)
