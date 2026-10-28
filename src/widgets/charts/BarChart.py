from PySide6 import QtCharts
from PySide6.QtGui import QColor, QCursor, QFont, QPainter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolTip

from src.services.ChartService import ChartService

from src.widgets.charts.ChartPalette import ChartPalette

class BarChart(QtCharts.QChartView):
    def __init__(self):
        super(BarChart, self).__init__()

        self.title = 'Ingresos y gastos por mes'
        self.chart_palette = ChartPalette()
        self.chart_info = None

        self.chart_service = ChartService()

        self.setRenderHint(QPainter.Antialiasing)

    def reload(self, filter):
        chart_info = self.chart_service.get_chart_info('bar', filter)
        self.chart_info = chart_info

        bar_series = QtCharts.QBarSeries()
        bar_series.append(self.create_bar_set('Ingresos', chart_info['incomes'], ChartPalette.INCOME))
        bar_series.append(self.create_bar_set('Gastos', chart_info['amounts'], ChartPalette.EXPENSE))

        chart = QtCharts.QChart()
        chart.addSeries(bar_series)
        chart.setTitle(self.get_title(chart_info))

        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append(chart_info['short_months'])

        font_angle, font_size = self.get_font_features(chart_info['amounts'])
        axis_x.setLabelsAngle(font_angle)
        axis_x.setLabelsFont(QFont('Monospace', font_size))
        axis_x.setGridLineVisible(False)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        bar_series.attachAxis(axis_x)

        axis_y = QtCharts.QValueAxis()
        axis_y.setLabelFormat('%.0f')
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        bar_series.attachAxis(axis_y)
        axis_y.applyNiceNumbers()

        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.setChart(chart)

        return chart_info

    def create_bar_set(self, name, amounts, color):
        bar_set = QtCharts.QBarSet(name)
        bar_set.setColor(QColor(color))
        bar_set.setBorderColor(QColor(color))
        bar_set.append(amounts)
        bar_set.hovered.connect(lambda status, index: self.bar_hovered(name, amounts, status, index))

        return bar_set

    def bar_hovered(self, name, amounts, status, index):
        if not status:
            QToolTip.hideText()
            return

        month = self.chart_info['months'][index]
        balance = self.chart_info['incomes'][index] - self.chart_info['amounts'][index]

        QToolTip.showText(QCursor.pos(), f'{month}\n{name}: {self.chart_palette.format_amount(amounts[index])}\nBalance del mes: {self.chart_palette.format_amount(balance)}')

    def get_title(self, chart_info):
        amount = round(sum(chart_info['amounts']), 2)

        return f"{self.title} (gastos: {self.chart_palette.format_amount(amount)})"

    def get_font_features(self, values):
        values_no = len(values)

        if values_no < 9:
            font_size = 12
            font_angle = 0
        else:
            font_size = 11
            font_angle = 90

        return font_angle, font_size
