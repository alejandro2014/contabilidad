from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from src.widgets.FilterWidget import FilterWidget

from src.widgets.charts.BarChart import BarChart
from src.widgets.charts.PieChart import PieChart
from src.widgets.RootWidget import RootWidget

from globals import widgets_pool as wpool

class ViewChartsScreen(RootWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.widget_ids = ['pie-chart', 'savings-chart', 'incomes-chart', 'filter-widget']

    def create_layout(self):
        layout = QVBoxLayout()

        column_left = QVBoxLayout()
        column_left.addWidget(self.pie_chart)

        column_right = QVBoxLayout()
        column_right.addWidget(self.savings_chart)
        column_right.addWidget(self.incomes_chart)

        charts_layout = QHBoxLayout()
        charts_layout.addLayout(column_left)
        charts_layout.addLayout(column_right)

        layout.addWidget(self.filter_widget)
        layout.addLayout(charts_layout)

        self.setLayout(layout)

    def init_widgets(self):
        self.reload_charts()

    def reload_charts(self):
        if hasattr(self, 'filter_widget') and self.filter_widget is not None:
            filter = self.filter_widget.filter

            self.pie_chart.reload(filter)
            self.savings_chart.reload(filter)
            self.incomes_chart.reload(filter)

            wpool.execute('filter-widget', 'set_visibility_charts')
