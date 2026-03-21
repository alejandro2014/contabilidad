from PySide2 import QtWidgets, QtGui
from PySide2.QtWidgets import QDialog

from src.config.ConfigLoader import ConfigLoader

from src.dialogs.AddCategoryDialog import AddCategoryDialog
from src.dialogs.BaseDialog import BaseDialog

from src.services.ExpenseTypesService import ExpenseTypesService

from src.widgets.BaseWidget import BaseWidget

from globals import widgets_pool as wpool

class ConfigureExpensesDialog(BaseDialog):
    def __init__(self, parent):
        self.id = 'configure-expenses-dialog'

        super(ConfigureExpensesDialog, self).__init__(parent, self.id)

        self.expense_types_service = ExpenseTypesService()

        self.table_info = ConfigLoader().load_table('expense-types')

        expense_types = self.expense_types_service.select_expense_types_full()

        self.table = self.create_table(self.table_info, expense_types)

        self.button_box = self.create_button_box(self.id)

        self.create_layout()
        self.show()

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.table)
        layout.addLayout(self.button_box)

        self.setLayout(layout)

    def add_category(self):
        add_category_dialog = AddCategoryDialog(self)

    def refresh(self):
        expense_types = self.expense_types_service.select_expense_types_full()

        self.populate(expense_types)

    def populate(self, table_rows):
        self.table.clearContents()

        categories = list(map(lambda x: x['field'], self.table_info))

        for index_row, table_row in enumerate(table_rows):
            self.table.insertRow(index_row)

            for index_category, category in enumerate(categories):
                self.table.setItem(index_row, index_category, QtWidgets.QTableWidgetItem(table_row[category]))

        self.table.resizeColumnsToContents()

    def remove_selected_rows(self):
        indexes = list(map(lambda x: x.row(), self.table.selectedIndexes()))
        indexes.sort(reverse=True)

        for i in indexes:
            category_text = self.table.item(i, 0).text()

            self.table.removeRow(i)
            self.expense_types_service.remove_category(category_text)

        wpool.execute('classifier', 'refresh')
