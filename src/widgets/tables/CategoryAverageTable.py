from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QGroupBox, QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from src.services.ChartService import ChartService

from src.widgets.charts.ChartPalette import ChartPalette

class CategoryAverageTable(QWidget):
    # Double clicking a row opens the movements of its category in the month, with this filter
    open_expenses = Signal(dict)

    def __init__(self, *args, **kwargs):
        super(CategoryAverageTable, self).__init__(*args, **kwargs)

        self.chart_service = ChartService()
        self.chart_palette = ChartPalette()
        self.filter = None
        self.average_info = None

        self.table = QTableWidget(0, 4)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        # The category takes the space left by the amounts
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.cellDoubleClicked.connect(self.row_double_clicked)

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.table)

        self.group_box = QGroupBox()
        self.group_box.setLayout(inner_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.group_box)
        self.setLayout(layout)

    def reload(self, filter):
        self.filter = filter
        self.average_info = self.chart_service.get_category_average_info(filter)

        self.table.setRowCount(0)

        if self.average_info is None:
            self.group_box.setTitle('Gasto del mes vs. media')
            return self.average_info

        self.group_box.setTitle(f"{self.average_info['month']} vs. media de los {self.average_info['months_no']} meses anteriores")
        self.table.setHorizontalHeaderLabels([ 'Tipo de gasto', 'Media mensual', self.average_info['month'], 'Diferencia' ])

        for index_row, row in enumerate(self.average_info['rows']):
            self.table.insertRow(index_row)

            category_item = QTableWidgetItem(row['category'])
            category_item.setToolTip(f"{row['category']}\nDoble clic para ver los movimientos del mes")
            self.table.setItem(index_row, 0, category_item)
            self.table.setItem(index_row, 1, self.amount_item(self.chart_palette.format_amount(row['average'])))
            self.table.setItem(index_row, 2, self.amount_item(self.chart_palette.format_amount(row['current'])))

            difference_item = self.amount_item(self.difference_text(row))
            # Spending more than the average is the bad side, always with its sign
            if row['difference'] != 0:
                difference_item.setForeground(QColor(ChartPalette.CRITICAL if row['difference'] > 0 else ChartPalette.GOOD))
            self.table.setItem(index_row, 3, difference_item)

        for column in [ 1, 2, 3 ]:
            self.table.resizeColumnToContents(column)

        return self.average_info

    def difference_text(self, row):
        difference = row['difference']
        text = self.chart_palette.format_amount(difference)
        text = f'+{text}' if difference > 0 else text

        if row['percentage'] is None:
            return text

        return f"{text} ({round(row['percentage']):+d} %)"

    def amount_item(self, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return item

    def row_double_clicked(self, row, column):
        category = self.average_info['rows'][row]['category']

        self.open_expenses.emit(self.chart_service.expenses_filter(self.filter, self.average_info['year_month'], category))
