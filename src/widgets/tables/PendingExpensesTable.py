import copy
from PySide2 import QtWidgets

from src.events.ListenerNode import ListenerNode

from src.services.PendingExpensesService import PendingExpensesService

from DateConverter import DateConverter
from src.config.ConfigLoader import ConfigLoader

class PendingExpensesTable(QtWidgets.QTableWidget, ListenerNode):
    def __init__(self, listeners_pool):
        ListenerNode.__init__(self, 'pending-expenses-table', listeners_pool)

        self.expenses_service = PendingExpensesService()
        self.expenses = []

        self.table_info = ConfigLoader().load_table('pending-expenses')
        column_labels = list(map(lambda x: x['field_text'], self.table_info))

        super().__init__(1, len(self.table_info))

        self.setHorizontalHeaderLabels(column_labels)

    def refresh_rows(self, filter = None):
        self.expenses = self.expenses_service.get_expenses(filter)

        expenses = copy.deepcopy(self.expenses)
        expenses = list(map(lambda ex: self.format_expense(ex), expenses))

        self.populate(expenses)
        self.send_event('sum-text', 'update_expenses_sum_from_table', expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

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
