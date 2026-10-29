from PySide6 import QtCharts
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtWidgets import QGraphicsSimpleTextItem, QPushButton

from src.services.ChartService import ChartService

from src.widgets.charts.ChartPalette import ChartPalette

class PieChart(QtCharts.QChartView):
    TITLE = 'Gastos por categoría'

    # Clicking a merchant opens its movements, with this filter
    open_expenses = Signal(dict)

    def __init__(self):
        super().__init__()

        self.chart_service = ChartService()
        self.chart_palette = ChartPalette()

        self.series = None
        self.filter = None
        # Color of each category, shared with the other charts so a category looks the same in all of them
        self.colors = {}
        # Each click on a slice adds a level: the merchants of a category, or what is inside "Otros".
        # A level is { 'title', 'kind' ('category' or 'merchant'), 'items' (every name with its amount) }
        self.levels = []

        self.setRenderHint(QPainter.Antialiasing)

        self.back_button = QPushButton('← Volver', self)
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setToolTip('Volver al gráfico anterior (también con clic derecho o Esc)')
        self.back_button.move(8, 8)
        self.back_button.clicked.connect(self.zoom_out)
        self.back_button.hide()

        # The amount of the current chart, written in the hole of the middle
        self.total_label = QGraphicsSimpleTextItem(self.chart())
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.total_label.setFont(font)
        self.chart().plotAreaChanged.connect(self.center_total_label)

    def reload(self, filter):
        self.filter = filter
        chart_info = self.chart_service.get_chart_info('pie', filter)

        # Before showing the series, as the theme would change their colors
        self.chart_palette.apply_theme(self.chart())

        # Other dates change what is inside every slice, so it starts again from the categories
        self.levels = [ { 'title': self.TITLE, 'kind': 'category', 'items': chart_info } ]

        categories = self.group(chart_info)
        self.colors = self.chart_palette.category_colors(categories)

        self.show_level()

        self.chart().legend().setAlignment(Qt.AlignRight)

        return chart_info

    def group(self, items):
        return self.chart_service.formatter.group_categories(items, len(ChartPalette.SERIES))

    def show_level(self):
        chart = self.chart()
        level = self.levels[-1]

        if self.series:
            chart.removeSeries(self.series)

        slices = self.group(level['items'])
        # The categories keep the colors of the other charts, the zoomed levels have their own
        colors = self.colors if len(self.levels) == 1 else self.chart_palette.category_colors(slices)
        self.series = self.compose_series(slices, colors)

        chart.addSeries(self.series)
        chart.setTitle(' › '.join([ level['title'] for level in self.levels ]))

        self.back_button.setVisible(len(self.levels) > 1)

        self.total_label.setBrush(chart.titleBrush())
        self.total_label.setText(self.chart_palette.format_amount(sum(slices.values())))
        self.center_total_label()

    def center_total_label(self):
        # The pie is centered in the plot area
        center = self.chart().plotArea().center()
        rect = self.total_label.boundingRect()
        self.total_label.setPos(center.x() - rect.width() / 2, center.y() - rect.height() / 2)

    def compose_series(self, categories, colors):
        series = QtCharts.QPieSeries()
        # A hole in the middle makes the slices easier to compare
        series.setHoleSize(0.35)
        total = sum(categories.values())
        # The gap has the color of the background, light or dark
        gap_color = self.chart_palette.background_color(self.chart())

        for i, category_name in enumerate(categories):
            amount = categories[category_name]
            title = self.get_chart_slice_title(category_name, amount, total)
            series.append(title, amount)

            slice = series.slices()[i]
            slice.setBrush(colors[category_name])
            # A thin gap between the slices
            slice.setPen(QPen(gap_color, 2))
            slice.clicked.connect(lambda name=category_name: self.zoom_in(name))
            slice.hovered.connect(lambda state, slice=slice, name=category_name: self.slice_hovered(slice, name, state))

        return series

    def is_others(self, name):
        # "Otros" is not one of the items when it groups the smallest ones
        return name not in self.levels[-1]['items']

    def zoom_in(self, name):
        level = self.levels[-1]

        if self.is_others(name):
            # The small items grouped in "Otros", of the same kind as the ones of this level
            shown = list(self.group(level['items']).keys())
            items = { item: amount for item, amount in level['items'].items() if item not in shown }
            self.levels.append({ 'title': name, 'kind': level['kind'], 'items': items })
        elif level['kind'] == 'category':
            items = self.chart_service.get_merchants_info(self.filter, name)
            self.levels.append({ 'title': name, 'kind': 'merchant', 'items': items })
        else:
            self.open_merchant_expenses(name)
            return

        self.unsetCursor()
        self.show_level()

    def open_merchant_expenses(self, merchant):
        # The category is the level where its merchants start, before any "Otros" of the merchants
        category = next(level['title'] for level in self.levels if level['kind'] == 'merchant')

        self.open_expenses.emit(self.chart_service.expenses_filter(self.filter, category = category, search_value = merchant))

    def zoom_out(self):
        if len(self.levels) <= 1:
            return

        self.levels.pop()
        self.show_level()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.zoom_out()
            return

        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in [ Qt.Key_Escape, Qt.Key_Backspace ]:
            self.zoom_out()
            return

        super().keyPressEvent(event)

    def slice_hovered(self, slice, name, state):
        slice.setExploded(state)
        slice.setLabelVisible(state)

        # Every slice can be clicked: the categories and "Otros" show what is inside, the merchants their movements
        if state:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.unsetCursor()

    def get_chart_slice_title(self, category_name, amount, total):
        percentage = round(amount / total * 100.0, 1)

        return f'{category_name}: {self.chart_palette.format_amount(amount)} ({percentage}%)'
