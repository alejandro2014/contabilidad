from PySide2.QtWidgets import QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

from src.widgets.FilterWidget import FilterWidget

from src.widgets.charts.BarChart import BarChart
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

        self.pie_chart = PieChart()
        self.bar_chart = BarChart()
        
        self.layout.addWidget(self.pie_chart)
        self.layout.addWidget(self.bar_chart)

        self.reload_charts(self.filter)

    def reload_charts(self, filter):
        chart_info = self.pie_chart.reload(filter)
        self.bar_chart.reload(filter)

        self.send_event('sum-text', 'update_expenses_sum_from_chart', chart_info)
        self.send_event('sum-text', 'hide_records_no')
        return
        chart_types = ['pie', 'bar']

        for chart_type in chart_types:
            self.reload_chart(chart_type, filter)

    def reload_chart(self, chart_type, filter):
        chart_info = self.chart_service.get_chart_info(chart_type, filter)

        if chart_info is None:
            return
        
        self.pie_chart.reload(chart_info)

        if chart_type == 'pie':
            self.send_event('sum-text', 'update_expenses_sum_from_chart', chart_info)
            self.send_event('sum-text', 'hide_records_no')
