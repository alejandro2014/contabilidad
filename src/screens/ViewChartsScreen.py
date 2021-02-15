from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

from src.services.ChartService import ChartService
from src.widgets.FilterWidget import FilterWidget
from src.widgets.charts.PieChart import PieChart

class ViewChartsScreen(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(ViewChartsScreen, self).__init__(*args, **kwargs)

        self.listeners_pool = listeners_pool
        ListenerNode.__init__(self, 'view-charts-screen', self.listeners_pool)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.filter_widget = FilterWidget('chart', listeners_pool)
        self.layout.addWidget(self.filter_widget)

        self.filter = self.filter_widget.filter

        self.chart_service = ChartService()

        self.pie_chart = PieChart()
        self.layout.addWidget(self.pie_chart)

        self.reload_charts(self.filter)

    def reload_charts(self, filter):
        pie_chart_info = self.chart_service.get_pie_chart_info(filter)

        if pie_chart_info == {}:
            return
            
        self.pie_chart.reload(pie_chart_info)

        self.send_event('sum-text', 'update_expenses_sum_from_chart', pie_chart_info)
        self.send_event('sum-text', 'hide_records_no')
