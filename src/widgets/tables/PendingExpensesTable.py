import copy

from DateConverter import DateConverter

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from src.config.ConfigLoader import ConfigLoader
from src.events.ListenerNode import ListenerNode
from src.services.expenses_service import ExpensesService

class SortableItem(QTableWidgetItem):
    # Sorts by a value different from the text shown (raw date, numeric amount...)
    def __init__(self, text, sort_key):
        super().__init__(text)
        self.sort_key = sort_key

    def __lt__(self, other):
        return self.sort_key < other.sort_key

class PendingExpensesTable(QTableWidget, ListenerNode):
    def __init__(self, listeners_pool):
        ListenerNode.__init__(self, 'pending-expenses-table', listeners_pool)

        self.expenses_service = ExpensesService()
        self.expenses = []
        self.current_filter = None

        self.table_info = ConfigLoader().load_table('pending-expenses')
        column_labels = [ ti['field_text'] for ti in self.table_info ]

        super().__init__(1, len(self.table_info))

        self.setHorizontalHeaderLabels(column_labels)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Clicking on a header sorts by that column. Initially sorted by amount, as they come from the database
        self.horizontalHeader().setSortIndicator(2, Qt.SortOrder.AscendingOrder)
        self.setSortingEnabled(True)

    def refresh_rows(self, filter = None):
        self.current_filter = filter
        self.expenses = self.expenses_service.get_pending_expenses(filter, sort_by='amount')
        
        expenses = copy.deepcopy(self.expenses)

        self.populate(expenses)

        self.send_event('sum-text', 'update_expenses_sum_from_table', expenses)
        self.send_event('sum-text', 'set_records_no_value', len(expenses))

    def populate(self, expenses):
        # With sorting enabled the rows would move while they are being filled
        self.setSortingEnabled(False)
        self.setRowCount(0)

        for index_row, expense in enumerate(expenses):
            self.insertRow(index_row)

            formatted_date = DateConverter().format_pretty(expense.date)
            date_item = SortableItem(formatted_date, expense.date)
            date_item.setData(Qt.ItemDataRole.UserRole, expense.id)
            self.setItem(index_row, 0, date_item)

            self.setItem(index_row, 1, SortableItem(expense.title, expense.title.lower()))

            formatted_amount = str(expense.amount)
            self.setItem(index_row, 2, SortableItem(formatted_amount, float(expense.amount)))

        # Sorts again by the column chosen by the user
        self.setSortingEnabled(True)

        self.resizeColumnsToContents()

    def get_current_expenses(self, value = None):
        return self.expenses
    
    def classify_selected(self, category):
        indexes = self.get_selected_indexes()

        if len(indexes) == 0:
            return

        # The rows may be sorted differently than self.expenses, so the id is taken from the row
        expense_ids = [ self.item(i, 0).data(Qt.ItemDataRole.UserRole) for i in indexes ]

        self.expenses_service.classify_expenses(expense_ids, category)
        self.refresh_rows(self.current_filter)

        # The classified rows are gone, so the next one is now where the first of them was
        self.select_row(min(indexes))
        self.setFocus()

    def select_row(self, row):
        row = min(row, self.rowCount() - 1)

        if row < 0:
            return

        self.selectRow(row)
        self.scrollToItem(self.item(row, 0))

    def keyPressEvent(self, event):
        # Enter classifies the selected rows with the type of the combo, and typing a letter looks for a type
        if event.key() in [ Qt.Key.Key_Return, Qt.Key.Key_Enter ]:
            self.send_event('classificator', 'classify_elements')
            return

        with_modifier = event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.AltModifier)

        if event.text().strip() != '' and not with_modifier:
            self.send_event('classificator', 'type_ahead', event.text())
            return

        super().keyPressEvent(event)
    
    def get_selected_indexes(self):
        selected_indexes = self.selectedIndexes()

        return sorted(list(set([ si.row() for si in selected_indexes ])), reverse=True)
    
