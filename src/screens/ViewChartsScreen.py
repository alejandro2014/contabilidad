from PySide6.QtCore import QEvent, QMarginsF, QPoint, QRectF
from PySide6.QtGui import QPageLayout, QPageSize, QPainter, QPdfWriter
from PySide6.QtWidgets import QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from DateConverter import DateConverter

from src.config.settings import app_settings

from src.dialogs.InfoDialog import InfoDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.events.ListenerNode import ListenerNode

from src.services.ChartService import ChartService
from src.services.ExportService import ExportService

from src.widgets.FilterWidget import FilterWidget
from src.widgets.KpiCards import KpiCards

from src.widgets.charts.ChartPalette import ChartPalette
from src.widgets.charts.BalanceChart import BalanceChart
from src.widgets.charts.BarChart import BarChart
from src.widgets.charts.EvolutionChart import EvolutionChart
from src.widgets.charts.PieChart import PieChart

from src.widgets.tables.CategoryAverageTable import CategoryAverageTable
from src.widgets.tables.TopExpensesTable import TopExpensesTable

class ViewChartsScreen(QWidget, ListenerNode):
    CHART_MIN_HEIGHT = 340

    # Periods the KPI cards can be compared with, and the setting with the one chosen
    COMPARISONS = [ ('Periodo anterior', 'previous'), ('Mismo periodo del año pasado', 'last_year'), ('No comparar', None) ]
    COMPARISON_SETTING = 'dashboard/comparison'

    def __init__(self, listeners_pool, *args, **kwargs):
        super(ViewChartsScreen, self).__init__(*args, **kwargs)

        self.listeners_pool = listeners_pool
        ListenerNode.__init__(self, 'view-charts-screen', self.listeners_pool)

        self.chart_service = ChartService()
        self.export_service = ExportService()
        self.chart_palette = ChartPalette()
        # The charts are drawn again when the system changes between light and dark mode
        self.dark = self.chart_palette.is_dark()
        # What every chart shows, to export it
        self.dashboard = None

        # The dashboard is taller than small windows, so it scrolls
        self.content = QWidget()
        self.layout = QVBoxLayout()
        self.content.setLayout(self.layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(self.content)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        # The charts must exist before the filter widget, as it reloads them when created
        self.comparison_combo = self.create_comparison_combo()
        self.kpi_cards = KpiCards()
        self.kpi_cards.pending_button.clicked.connect(lambda: self.send_event('main-window', 'classify_expenses'))
        self.pie_chart = PieChart()
        self.bar_chart = BarChart()
        self.evolution_chart = EvolutionChart()
        self.top_expenses_table = TopExpensesTable()
        self.balance_chart = BalanceChart()
        self.category_average_table = CategoryAverageTable()

        # Clicking a part of a chart opens the table with its movements
        for widget in [ self.pie_chart, self.bar_chart, self.evolution_chart, self.top_expenses_table, self.category_average_table ]:
            widget.open_expenses.connect(self.open_expenses)

        self.filter_widget = FilterWidget('chart', listeners_pool)
        self.layout.addWidget(self.filter_widget)

        self.filter = self.filter_widget.filter

        self.layout.addLayout(self.create_options_layout())
        self.layout.addWidget(self.kpi_cards)

        charts_layout = QGridLayout()
        # Same width for both columns
        charts_layout.addWidget(self.pie_chart, 0, 0)
        charts_layout.addWidget(self.bar_chart, 0, 1)
        charts_layout.addWidget(self.evolution_chart, 1, 0)
        charts_layout.addWidget(self.top_expenses_table, 1, 1)
        charts_layout.addWidget(self.category_average_table, 2, 0)
        charts_layout.addWidget(self.balance_chart, 2, 1)
        charts_layout.setColumnStretch(0, 1)
        charts_layout.setColumnStretch(1, 1)

        for widget in [ self.pie_chart, self.bar_chart, self.evolution_chart, self.top_expenses_table, self.category_average_table, self.balance_chart ]:
            widget.setMinimumHeight(self.CHART_MIN_HEIGHT)

        self.layout.addLayout(charts_layout)

        self.reload_charts(self.filter)

    def create_comparison_combo(self):
        combo = QComboBox()

        for text, comparison in self.COMPARISONS:
            combo.addItem(text, comparison)

        saved = app_settings().value(self.COMPARISON_SETTING, 'previous')
        combo.setCurrentIndex(max(combo.findData(None if saved == 'none' else saved), 0))
        combo.currentIndexChanged.connect(self.comparison_changed)

        return combo

    def create_options_layout(self):
        export_button = WidgetCreator().create_button('Exportar', 'upload', self.export_dashboard)

        layout = QHBoxLayout()
        layout.addWidget(QLabel('Comparar con:'))
        layout.addWidget(self.comparison_combo)
        layout.addStretch()
        layout.addWidget(export_button)

        return layout

    def comparison_changed(self, index):
        comparison = self.comparison_combo.currentData()
        app_settings().setValue(self.COMPARISON_SETTING, 'none' if comparison is None else comparison)

        self.reload_kpis(self.filter)

    def changeEvent(self, event):
        super().changeEvent(event)

        # The palette also changes for other reasons, and the charts are only drawn again for the mode
        if event.type() == QEvent.Type.PaletteChange and self.chart_palette.is_dark() != self.dark:
            self.dark = self.chart_palette.is_dark()
            self.reload_charts(self.filter)

    def reload_charts(self, filter):
        pie_chart_info = self.pie_chart.reload(filter)
        bar_chart_info = self.bar_chart.reload(filter)

        # Same colors as the pie chart for the same categories
        evolution_info = self.evolution_chart.reload(filter, self.pie_chart.colors)
        top_expenses = self.top_expenses_table.reload(filter)
        average_info = self.category_average_table.reload(filter)
        balance_info = self.balance_chart.reload(filter)

        self.dashboard = {
            'categories': pie_chart_info,
            'bar': bar_chart_info,
            'evolution': evolution_info,
            'top': top_expenses,
            'average': average_info,
            'balance': balance_info
        }

        self.reload_kpis(filter)

        # The pie chart leaves out the categories with more refunds than expenses, so the bar chart has the real total
        self.send_event('sum-text', 'update_expenses_sum_from_chart', bar_chart_info['amounts'])
        self.send_event('sum-text', 'hide_records_no')

    def reload_kpis(self, filter):
        comparison = self.comparison_combo.currentData()
        kpis = self.chart_service.get_kpis(filter, self.dashboard['categories'], self.dashboard['bar'], comparison)

        self.dashboard['kpis'] = kpis
        self.kpi_cards.reload(kpis, comparison)

    def open_expenses(self, filter):
        self.send_event('main-window', 'open_expenses_table', filter)

    def export_dashboard(self):
        file_name, selected_filter = QFileDialog.getSaveFileName(self, 'Exportar panel', 'panel.pdf', 'PDF (*.pdf);;Excel (*.xlsx)')

        if file_name == '':
            return

        # The format is the one of the extension, or of the type chosen when it is typed without it
        if not file_name.lower().endswith(('.pdf', '.xlsx')):
            file_name += '.xlsx' if 'xlsx' in selected_filter.lower() else '.pdf'

        if file_name.lower().endswith('.xlsx'):
            self.export_excel(file_name)
        else:
            self.export_pdf(file_name)

        InfoDialog(self, title = 'Panel exportado', message = f'Se ha guardado en {file_name}')

    def export_excel(self, file_name):
        date_converter = DateConverter()
        dashboard = dict(self.dashboard)
        dashboard['date_from'] = date_converter.format_pretty(self.filter['date']['from'])
        dashboard['date_to'] = date_converter.format_pretty(self.filter['date']['to'])

        self.export_service.export_sheets(file_name, self.chart_service.formatter.format_dashboard_sheets(dashboard))

    def export_pdf(self, file_name):
        # The dashboard as it is shown, in a single page of the same proportions
        writer = QPdfWriter(file_name)
        writer.setPageLayout(QPageLayout(QPageSize(QPageSize.PageSizeId.A4), QPageLayout.Orientation.Portrait, QMarginsF(10, 10, 10, 10)))
        writer.setTitle('Contabilidad')

        painter = QPainter(writer)

        try:
            page = QRectF(painter.viewport())
            scale = min(page.width() / self.content.width(), page.height() / self.content.height())
            painter.scale(scale, scale)
            self.content.render(painter, QPoint())
        finally:
            painter.end()
