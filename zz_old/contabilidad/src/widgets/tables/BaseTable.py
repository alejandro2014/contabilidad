import copy
from PySide2 import QtWidgets

from src.services.ClassifiedExpensesService import ClassifiedExpensesService

from src.misc.DateConverter import DateConverter

from globals import widgets_pool as wpool

class BaseTable(QtWidgets.QTableWidget):
    def __init__(self, table_name, table_info):
        super().__init__(1, len(table_info))

        self.set_table_labels(table_info)

    def set_table_labels(self, table_info):
        column_labels = list(map(lambda x: x['field_text'], table_info))
        self.setHorizontalHeaderLabels(column_labels)

    def populate(self, table_rows):
        self.clearContents()

        categories = list(map(lambda x: x['field'], self.table_info))

        for index_row, table_row in enumerate(table_rows):
            self.insertRow(index_row)

            for index_category, category in enumerate(categories):
                self.setItem(index_row, index_category, QtWidgets.QTableWidgetItem(table_row[category]))

        self.resizeColumnsToContents()

    def format_expense(self, expense):
        expense['date'] = DateConverter().format_pretty(expense['date'])

        return expense

    def get_current_expenses(self, value = None):
        return self.expenses
