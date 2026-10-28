from PySide6 import QtCharts
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen

from src.services.ChartService import ChartService

from src.widgets.charts.ChartPalette import ChartPalette

class PieChart(QtCharts.QChartView):
    def __init__(self):
        super().__init__()

        self.chart_service = ChartService()
        self.chart_palette = ChartPalette()

        self.series = None
        # Color of each category, shared with the other charts so a category looks the same in all of them
        self.colors = {}

        self.setRenderHint(QPainter.Antialiasing)

    def reload(self, filter):
        chart_info = self.chart_service.get_chart_info('pie', filter)
        chart = self.chart()

        if self.series:
            chart.removeSeries(self.series)

        categories = self.chart_service.formatter.group_categories(chart_info, len(ChartPalette.SERIES))
        self.colors = self.chart_palette.category_colors(categories)
        self.series = self.compose_series(categories)

        chart.addSeries(self.series)

        chart.setTitle('Gastos por categoría')

        chart.legend().setAlignment(Qt.AlignRight)

        return chart_info

    def compose_series(self, categories):
        series = QtCharts.QPieSeries()
        # A hole in the middle makes the slices easier to compare
        series.setHoleSize(0.35)
        total = sum(categories.values())

        for i, category_name in enumerate(categories):
            amount = categories[category_name]
            title = self.get_chart_slice_title(category_name, amount, total)
            series.append(title, amount)

            slice = series.slices()[i]
            slice.setBrush(self.colors[category_name])
            # A thin gap between the slices
            slice.setPen(QPen(Qt.GlobalColor.white, 2))

        series.hovered.connect(self.slice_hovered)

        return series

    def slice_hovered(self, slice, state):
        slice.setExploded(state)
        slice.setLabelVisible(state)

    def get_chart_slice_title(self, category_name, amount, total):
        percentage = round(amount / total * 100.0, 1)

        return f'{category_name}: {self.chart_palette.format_amount(amount)} ({percentage}%)'
