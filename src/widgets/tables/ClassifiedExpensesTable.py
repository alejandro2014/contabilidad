import copy
from PySide2 import QtWidgets

from src.events.ListenerNode import ListenerNode

from src.services.ClassifiedExpensesService import ClassifiedExpensesService

from DateConverter import DateConverter
from src.config.ConfigLoader import ConfigLoader

class ClassifiedExpensesTable(QtWidgets.QTableWidget, ListenerNode):
    def __init__(self, listeners_pool, table_type):
        self.listeners_pool = listeners_pool
        self.table_type = table_type
        self.table_id = 'classified-expenses-table'
        self.expenses_service = ClassifiedExpensesService()
        self.expenses = []

        self.set_table_type(table_type)

    def set_table_type(self, table_type):
        if self.table_type == 'expenses_raw':
            self.init_table('classified-expenses')
        elif self.table_type == 'expenses_by_month':
            self.init_table('classified-expenses-by-month')
        elif self.table_type == 'expenses_by_type':
            self.init_table('classified-expenses-by-type')
        elif self.table_type == 'expenses_by_type_and_month':
            self.init_table('classified-expenses-by-type-and-month')

    def init_table(self, table_info_file):
        self.table_info = ConfigLoader().load_table(table_info_file)
        column_labels = list(map(lambda x: x['field_text'], self.table_info))

        ListenerNode.__init__(self, self.table_id, self.listeners_pool)
        super().__init__(1, len(self.table_info))

        self.setHorizontalHeaderLabels(column_labels)

    def refresh_rows(self, filter = None):
        if self.table_type == 'expenses_raw':
            self.refresh_expenses_raw(filter)
        elif self.table_type == 'expenses_by_month':
            self.refresh_expenses_by_month()
        elif self.table_type == 'expenses_by_type':
            self.refresh_expenses_by_type()
        elif self.table_type == 'expenses_by_type_and_month':
            self.refresh_expenses_by_type_and_month()

    def refresh_expenses_raw(self, filter):
        self.expenses = self.expenses_service.get_expenses(filter)

        expenses = copy.deepcopy(self.expenses)
        expenses = list(map(lambda ex: self.format_expense(ex), expenses))

        self.populate(expenses)
        self.send_event('sum-text', 'update_expenses_sum_from_table', expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def refresh_expenses_by_month(self):
        self.expenses = self.expenses_service.get_expenses_by_month()

        expenses = copy.deepcopy(self.expenses)

        self.populate(expenses)
        self.send_event('sum-text', 'update_expenses_sum_from_table', expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def refresh_expenses_by_type(self):
        self.expenses = self.expenses_service.get_expenses_by_type()

        expenses = copy.deepcopy(self.expenses)

        self.populate(expenses)
        self.send_event('sum-text', 'update_expenses_sum_from_table', expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def refresh_expenses_by_type_and_month(self):
        self.expenses = self.expenses_service.get_expenses_by_type_and_month()

        expenses = copy.deepcopy(self.expenses)

        self.populate(expenses)
        self.send_event('sum-text', 'update_expenses_sum_from_table', expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def populate(self, table_rows):
        #TODO This throws a runtime error but not critical. Fix it.
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
