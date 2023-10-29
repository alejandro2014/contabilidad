import copy

from DateConverter import DateConverter

from PySide2.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from src.config.ConfigLoader import ConfigLoader
from src.events.ListenerNode import ListenerNode
from src.services.expenses_service import ExpensesService

class PendingExpensesTable(QTableWidget, ListenerNode):
    def __init__(self, listeners_pool):
        ListenerNode.__init__(self, 'pending-expenses-table', listeners_pool)

        self.expenses_service = ExpensesService()
        self.expenses = []

        self.table_info = ConfigLoader().load_table('pending-expenses')
        column_labels = [ ti['field_text'] for ti in self.table_info ]

        super().__init__(1, len(self.table_info))

        self.setHorizontalHeaderLabels(column_labels)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def refresh_rows(self, filter = None):
        self.expenses = self.expenses_service.get_pending_expenses(filter)
        
        expenses = copy.deepcopy(self.expenses)

        self.populate(expenses)
        self.send_event('sum-text', 'update_expenses_sum_from_table', expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def populate(self, expenses):
        self.clearContents()

        for index_row, expense in enumerate(expenses):
            self.insertRow(index_row)

            formatted_date = DateConverter().format_pretty(expense.date)
            self.setItem(index_row, 0, QTableWidgetItem(formatted_date))

            self.setItem(index_row, 1, QTableWidgetItem(expense.title))

            formatted_amount = str(expense.amount)
            self.setItem(index_row, 2, QTableWidgetItem(formatted_amount))

        self.resizeColumnsToContents()

    def get_current_expenses(self, value = None):
        return self.expenses
    
    def classify_selected(self, category):
        indexes = self.get_selected_indexes()

        expenses = self.get_expenses_from_indexes(indexes)

        return

        self.expenses_service.classify_expenses(expenses, category)
        self.refresh_rows()
    
    def get_selected_indexes(self):
        selected_indexes = self.selectedIndexes()

        return sorted(list(set([ si.row() for si in selected_indexes ])), reverse=True)
    
    def get_expenses_from_indexes(self, indexes):
        expenses = []

        for index in indexes:
            expense = self.expenses[index]
            expense['quantity'] = float(expense['quantity'])

            expenses.append(expense)
        
        return expenses
