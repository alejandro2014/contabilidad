import copy
from PySide6 import QtWidgets

from DateConverter import DateConverter

from src.config.ConfigLoader import ConfigLoader
from src.events.ListenerNode import ListenerNode
from src.services.expenses_service import ExpensesService
from src.services.ExpenseTypesService import ExpenseTypesService

class ClassifiedExpensesTable(QtWidgets.QTableWidget, ListenerNode):
    def __init__(self, listeners_pool, table_type):
        self.listeners_pool = listeners_pool
        self.table_type = table_type
        self.table_id = 'classified-expenses-table'
        self.expenses_service = ExpensesService()
        self.expense_types_service = ExpenseTypesService()
        self.expenses = []
        self.current_filter = None

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
        column_labels = [ x['field_text'] for x in self.table_info ]

        ListenerNode.__init__(self, self.table_id, self.listeners_pool)
        super().__init__(1, len(self.table_info))

        self.setHorizontalHeaderLabels(column_labels)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

    def refresh_rows(self, filter = None):
        self.current_filter = filter

        if self.table_type == 'expenses_raw':
            self.refresh_expenses_raw(filter)
        elif self.table_type == 'expenses_by_month':
            self.refresh_expenses_by_month()
        elif self.table_type == 'expenses_by_type':
            self.refresh_expenses_by_type()
        elif self.table_type == 'expenses_by_type_and_month':
            self.refresh_expenses_by_type_and_month()

    def refresh_expenses_raw(self, filter):
        self.expenses = self.expenses_service.get_classified_expenses(filter)

        expenses = copy.deepcopy(self.expenses)
        expenses = [ self.format_expense(ex) for ex in expenses ]

        self.populate(expenses)
        self.send_expenses_sum(expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def refresh_expenses_by_month(self):
        self.expenses = self.expenses_service.get_classified_expenses_by_month()

        expenses = copy.deepcopy(self.expenses)

        self.populate(expenses)
        self.send_expenses_sum(expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def refresh_expenses_by_type(self):
        self.expenses = self.expenses_service.get_classified_expenses_by_type()

        expenses = copy.deepcopy(self.expenses)

        self.populate(expenses)
        self.send_expenses_sum(expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def refresh_expenses_by_type_and_month(self):
        self.expenses = self.expenses_service.get_classified_expenses_by_type_and_month()

        expenses = copy.deepcopy(self.expenses)

        self.populate(expenses)
        self.send_expenses_sum(expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def send_expenses_sum(self, expenses):
        # Incomes and not computed types are shown in the table, but they are not money spent
        not_computed_categories = self.expense_types_service.get_not_computed_categories()
        amounts = [ ex['quantity'] for ex in expenses if ex.get('type') not in not_computed_categories ]

        self.send_event('sum-text', 'update_expenses_sum_from_amounts', amounts)

    def populate(self, table_rows):
        self.setRowCount(0)

        categories = [ x['field'] for x in self.table_info ]

        for index_row, table_row in enumerate(table_rows):
            self.insertRow(index_row)

            for index_category, category in enumerate(categories):
                self.setItem(index_row, index_category, QtWidgets.QTableWidgetItem(table_row[category]))

        self.resizeColumnsToContents()

    def format_expense(self, expense):
        return {
            'date': DateConverter().format_pretty(expense.date),
            'concept': expense.title,
            'type': expense.category,
            'quantity': str(expense.amount)
        }

    def unclassify_selected(self):
        # Only the raw table has one row per expense
        if self.table_type != 'expenses_raw':
            return

        rows = sorted(set([ si.row() for si in self.selectedIndexes() ]))
        expense_ids = [ self.expenses[r].id for r in rows ]

        if len(expense_ids) == 0:
            return

        self.expenses_service.unclassify_expenses(expense_ids)
        self.refresh_rows(self.current_filter)

    def get_current_expenses(self, value = None):
        return self.expenses
