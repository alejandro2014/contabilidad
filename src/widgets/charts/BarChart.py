from PySide2.QtCharts import QtCharts
from PySide2.QtGui import QFont, QPainter, QColor
from PySide2.QtCore import QPoint, Qt

from src.services.ChartService import ChartService

class BarChart(QtCharts.QChartView):
    def __init__(self):
        super(BarChart, self).__init__()

        self.title = 'Gastos por mes'
        self.color = QColor(100, 0, 0)

        self.chart_service = ChartService()

    def get_widgets_from_pool(self):
        pass

    def create_layout(self):
        pass

    def init_widgets(self):
        pass

    def reload(self, chart_info):
        chart_info = self.chart_service.get_chart_info('bar')

        bar_set = QtCharts.QBarSet("")
        bar_set.setColor(self.color)

        print(chart_info)
        bar_set.append(chart_info['amounts'])

        bar_series = QtCharts.QBarSeries()
        bar_series.append(bar_set)

        chart = QtCharts.QChart()
        chart.addSeries(bar_series)
        chart.setTitle(self.get_title(chart_info))

        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append(chart_info['months'])

        font_angle, font_size = self.get_font_features(chart_info['amounts'])
        axis_x.setLabelsAngle(font_angle)
        axis_x.setLabelsFont(QFont('Monospace', font_size))
        chart.setAxisX(axis_x, bar_series)

        axis_y = QtCharts.QValueAxis()
        chart.setAxisY(axis_y, bar_series)
        chart.legend().setVisible(False)

        self.setChart(chart)

    def get_title(self, chart_info):
        amount = round(sum(chart_info['amounts']), 2)

        return f"{self.title} ({amount}€)"

    def get_font_features(self, values):
        values_no = len(values)

        if values_no < 9:
            font_size = 10
            font_angle = 0
        else:
            font_size = 9
            font_angle = 90

        return font_angle, font_size
