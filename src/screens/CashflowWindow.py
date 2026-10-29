import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QFileDialog, QHBoxLayout, QLabel, QSplitter, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from src.dialogs.InfoDialog import InfoDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.CashflowService import CashflowService
from src.services.ComboBoxService import ComboBoxService
from src.widgets.charts.Treemap import Treemap

class CashflowWindow(QWidget):
    def __init__(self, parent):
        super(CashflowWindow, self).__init__(parent)

        # Separate window, but closed together with the main one
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle('Flujo de caja')
        self.resize(1600, 700)

        self.cashflow_service = CashflowService()
        self.widget_creator = WidgetCreator()

        self.header = [ 'Categoría' ] + ComboBoxService().get_months() + [ 'Total', 'Total %' ]
        # Rows shown in the table, with the indexes of the ones in bold (section titles, totals and balance)
        self.rows = []
        self.bold_rows = []
        # Sorting is applied inside each section, so incomes, expenses and totals keep their place
        self.cashflow = None
        self.sort_column = 0
        self.sort_order = Qt.SortOrder.AscendingOrder

        self.year_combo = self.widget_creator.create_combobox('year')
        self.year_combo.setCurrentText(str(datetime.date.today().year))

        self.group_by_combo = QComboBox()
        self.group_by_combo.addItem('Categoría del banco', 'bank')
        self.group_by_combo.addItem('Tipo de gasto', 'type')

        export_button = self.widget_creator.create_button('Exportar CSV', 'upload', self.export_csv)

        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel('Año:'))
        options_layout.addWidget(self.year_combo)
        options_layout.addWidget(QLabel('Agrupar por:'))
        options_layout.addWidget(self.group_by_combo)
        options_layout.addStretch()
        options_layout.addWidget(export_button)

        self.table = QTableWidget(0, len(self.header))
        self.table.setHorizontalHeaderLabels(self.header)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().setSortIndicator(self.sort_column, self.sort_order)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_by)

        # Share of each expense category, in the space left by the table
        self.treemap = Treemap()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.table)
        splitter.addWidget(self.treemap)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([ 4000, 1000 ])

        layout = QVBoxLayout()
        layout.addLayout(options_layout)
        layout.addWidget(splitter)
        self.setLayout(layout)

        self.year_combo.currentIndexChanged.connect(self.refresh)
        self.group_by_combo.currentIndexChanged.connect(self.refresh)

        self.refresh()

    def refresh(self, index = None):
        year = self.year_combo.currentText()
        group_by = self.group_by_combo.currentData()

        self.cashflow = self.cashflow_service.get_cashflow(year, group_by)

        self.show_cashflow()
        self.treemap.set_data([ (row[0], row[13]) for row in self.cashflow['expenses']['rows'] ])

    def sort_by(self, column):
        # Clicking the same column again reverses the order
        if column == self.sort_column and self.sort_order == Qt.SortOrder.AscendingOrder:
            self.sort_order = Qt.SortOrder.DescendingOrder
        else:
            self.sort_order = Qt.SortOrder.AscendingOrder

        self.sort_column = column
        self.table.horizontalHeader().setSortIndicator(self.sort_column, self.sort_order)

        self.show_cashflow()

    def show_cashflow(self):
        self.rows = []
        self.bold_rows = []

        self.add_section('Ingresos', self.cashflow['incomes'])
        self.add_empty_row()
        self.add_section('Gastos', self.cashflow['expenses'])
        self.add_empty_row()
        self.add_bold_row(self.cashflow['balance'])

        self.populate(self.rows)

    def add_section(self, title, section):
        descending = self.sort_order == Qt.SortOrder.DescendingOrder

        self.add_bold_row([ title ] + [ None ] * 14)
        self.rows += self.cashflow_service.sort_rows(section['rows'], self.sort_column, descending)
        self.add_bold_row(section['total'])

    def add_bold_row(self, row):
        self.bold_rows.append(len(self.rows))
        self.rows.append(row)

    def add_empty_row(self):
        self.rows.append([ '' ] + [ None ] * 14)

    def populate(self, rows):
        self.table.setRowCount(0)

        for index_row, row in enumerate(rows):
            self.table.insertRow(index_row)
            self.table.setItem(index_row, 0, QTableWidgetItem(row[0]))

            for index_column, amount in enumerate(row[1:14], 1):
                self.table.setItem(index_row, index_column, self.create_amount_item(amount))

            self.table.setItem(index_row, 14, self.create_amount_item(row[14], ' %'))

        for row in self.bold_rows:
            self.mark_bold_row(row)

        self.table.resizeColumnsToContents()

    def create_amount_item(self, amount, suffix = ''):
        text = '' if amount is None else f'{amount:.2f}{suffix}'

        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return item

    def mark_bold_row(self, row):
        font = QFont()
        font.setBold(True)

        for column in range(self.table.columnCount()):
            self.table.item(row, column).setFont(font)

    def export_csv(self):
        default_name = f'cashflow_{self.year_combo.currentText()}.csv'
        file_name, _ = QFileDialog.getSaveFileName(self, 'Exportar flujo de caja', default_name, 'CSV (*.csv)')

        if file_name == '':
            return

        self.cashflow_service.export_cashflow(file_name, self.header, self.rows)

        InfoDialog(self, title = 'Flujo de caja exportado', message = f'Se ha guardado en {file_name}')
