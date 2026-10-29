from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QGroupBox, QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from src.services.ChartService import ChartService

from src.widgets.charts.ChartPalette import ChartPalette

class TopExpensesTable(QWidget):
    HEADER = [ 'Fecha', 'Concepto', 'Tipo de gasto', 'Importe' ]

    # Double clicking a row opens the movements with its concept, with this filter
    open_expenses = Signal(dict)

    def __init__(self, *args, **kwargs):
        super(TopExpensesTable, self).__init__(*args, **kwargs)

        self.chart_service = ChartService()
        self.chart_palette = ChartPalette()
        self.filter = None
        self.expenses = []

        self.table = QTableWidget(0, len(self.HEADER))
        self.table.setHorizontalHeaderLabels(self.HEADER)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        # The concept takes the space left by the other columns
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.cellDoubleClicked.connect(self.row_double_clicked)

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.table)

        group_box = QGroupBox(f'Los {ChartService.TOP_EXPENSES_NO} mayores gastos')
        group_box.setLayout(inner_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(group_box)
        self.setLayout(layout)

    def reload(self, filter):
        expenses = self.chart_service.get_chart_info('top', filter)
        self.filter = filter
        self.expenses = expenses

        self.table.setRowCount(0)

        for index_row, expense in enumerate(expenses):
            self.table.insertRow(index_row)
            self.table.setItem(index_row, 0, QTableWidgetItem(expense['date']))
            # The concept is usually cut, so the whole text is shown when hovering it
            title_item = QTableWidgetItem(expense['title'])
            title_item.setToolTip(f"{expense['title']}\nDoble clic para ver los movimientos")
            self.table.setItem(index_row, 1, title_item)
            self.table.setItem(index_row, 2, QTableWidgetItem(expense['category']))

            amount_item = QTableWidgetItem(self.amount_text(expense))
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(index_row, 3, amount_item)

        for column in [ 0, 2, 3 ]:
            self.table.resizeColumnToContents(column)

        return expenses

    def amount_text(self, expense):
        text = self.chart_palette.format_amount(expense['amount'])

        # The repeated expenses show the amount of one of them and how many times it is repeated
        return text if expense['count'] == 1 else f"{text} ({expense['count']})"

    def row_double_clicked(self, row, column):
        expense = self.expenses[row]

        self.open_expenses.emit(self.chart_service.expenses_filter(self.filter, category = expense['category'], search_value = expense['title']))
