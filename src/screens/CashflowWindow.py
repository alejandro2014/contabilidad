import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QFileDialog, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from src.dialogs.InfoDialog import InfoDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.CashflowService import CashflowService
from src.services.ComboBoxService import ComboBoxService

class CashflowWindow(QWidget):
    def __init__(self, parent):
        super(CashflowWindow, self).__init__(parent)

        # Separate window, but closed together with the main one
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle('Flujo de caja')
        self.resize(1200, 600)

        self.cashflow_service = CashflowService()
        self.widget_creator = WidgetCreator()

        self.header = [ 'Categoría' ] + ComboBoxService().get_months() + [ 'Total' ]
        # Rows shown in the table, with the indexes of the ones in bold (section titles, totals and balance)
        self.rows = []
        self.bold_rows = []

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

        layout = QVBoxLayout()
        layout.addLayout(options_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.year_combo.currentIndexChanged.connect(self.refresh)
        self.group_by_combo.currentIndexChanged.connect(self.refresh)

        self.refresh()

    def refresh(self, index = None):
        year = self.year_combo.currentText()
        group_by = self.group_by_combo.currentData()

        cashflow = self.cashflow_service.get_cashflow(year, group_by)

        self.rows = []
        self.bold_rows = []

        self.add_section('Ingresos', cashflow['incomes'])
        self.add_empty_row()
        self.add_section('Gastos', cashflow['expenses'])
        self.add_empty_row()
        self.add_bold_row(cashflow['balance'])

        self.populate(self.rows)

    def add_section(self, title, section):
        self.add_bold_row([ title ] + [ None ] * 13)
        self.rows += section['rows']
        self.add_bold_row(section['total'])

    def add_bold_row(self, row):
        self.bold_rows.append(len(self.rows))
        self.rows.append(row)

    def add_empty_row(self):
        self.rows.append([ '' ] + [ None ] * 13)

    def populate(self, rows):
        self.table.setRowCount(0)

        for index_row, row in enumerate(rows):
            self.table.insertRow(index_row)
            self.table.setItem(index_row, 0, QTableWidgetItem(row[0]))

            for index_column, amount in enumerate(row[1:], 1):
                self.table.setItem(index_row, index_column, self.create_amount_item(amount))

        for row in self.bold_rows:
            self.mark_bold_row(row)

        self.table.resizeColumnsToContents()

    def create_amount_item(self, amount):
        text = '' if amount is None else f'{amount:.2f}'

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
