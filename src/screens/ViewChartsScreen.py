from PySide6.QtWidgets import QFrame, QGridLayout, QScrollArea, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

from src.services.ChartService import ChartService

from src.widgets.FilterWidget import FilterWidget
from src.widgets.KpiCards import KpiCards

from src.widgets.charts.BarChart import BarChart
from src.widgets.charts.EvolutionChart import EvolutionChart
from src.widgets.charts.PieChart import PieChart

from src.widgets.tables.TopExpensesTable import TopExpensesTable

class ViewChartsScreen(QWidget, ListenerNode):
    CHART_MIN_HEIGHT = 340

    def __init__(self, listeners_pool, *args, **kwargs):
        super(ViewChartsScreen, self).__init__(*args, **kwargs)

        self.listeners_pool = listeners_pool
        ListenerNode.__init__(self, 'view-charts-screen', self.listeners_pool)

        self.chart_service = ChartService()

        # The dashboard is taller than small windows, so it scrolls
        content = QWidget()
        self.layout = QVBoxLayout()
        content.setLayout(self.layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(content)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # The charts must exist before the filter widget, as it reloads them when created
        self.kpi_cards = KpiCards()
        self.pie_chart = PieChart()
        self.bar_chart = BarChart()
        self.evolution_chart = EvolutionChart()
        self.top_expenses_table = TopExpensesTable()

        self.filter_widget = FilterWidget('chart', listeners_pool)
        self.layout.addWidget(self.filter_widget)

        self.filter = self.filter_widget.filter

        self.layout.addWidget(self.kpi_cards)

        charts_layout = QGridLayout()
        # Same width for both columns
        charts_layout.addWidget(self.pie_chart, 0, 0)
        charts_layout.addWidget(self.bar_chart, 0, 1)
        charts_layout.addWidget(self.evolution_chart, 1, 0)
        charts_layout.addWidget(self.top_expenses_table, 1, 1)
        charts_layout.setColumnStretch(0, 1)
        charts_layout.setColumnStretch(1, 1)

        for widget in [ self.pie_chart, self.bar_chart, self.evolution_chart, self.top_expenses_table ]:
            widget.setMinimumHeight(self.CHART_MIN_HEIGHT)

        self.layout.addLayout(charts_layout)

        self.reload_charts(self.filter)

    def reload_charts(self, filter):
        pie_chart_info = self.pie_chart.reload(filter)
        bar_chart_info = self.bar_chart.reload(filter)

        # Same colors as the pie chart for the same categories
        self.evolution_chart.reload(filter, self.pie_chart.colors)
        self.top_expenses_table.reload(filter)

        self.kpi_cards.reload(self.chart_service.get_kpis(filter, pie_chart_info, bar_chart_info))

        # The pie chart leaves out the categories with more refunds than expenses, so the bar chart has the real total
        self.send_event('sum-text', 'update_expenses_sum_from_chart', bar_chart_info['amounts'])
        self.send_event('sum-text', 'hide_records_no')
