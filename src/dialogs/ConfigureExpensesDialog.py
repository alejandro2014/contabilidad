from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from src.config.ConfigLoader import ConfigLoader

from src.dialogs.AddCategoryDialog import AddCategoryDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.ExpenseTypesService import ExpenseTypesService
from src.services.LoadFileService import LoadFileService

class ConfigureExpensesDialog(QDialog):
    def __init__(self, parent, listeners_pool):
        super(ConfigureExpensesDialog, self).__init__(parent)

        self.listeners_pool = listeners_pool

        self.widget_creator = WidgetCreator()
        self.usecases_service = LoadFileService()
        self.expense_types_service = ExpenseTypesService()

        self.previous_value = None

        self.setWindowTitle("Configuración de categorías")
        self.resize(600, 400)
        self.setModal(True)

        table_info = ConfigLoader().load_table('expense-types')

        expense_types = self.expense_types_service.select_expense_types_full()

        self.table = self.widget_creator.create_table(table_info, expense_types)
        self.table.cellChanged.connect(self.cellChanged)
        self.table.cellClicked.connect(self.cellClicked)

        button_add = self.widget_creator.create_button("Añadir categoría", "upload", self.add_category)
        button_remove = self.widget_creator.create_button("Eliminar seleccionadas", "bin", self.remove_selected_rows)
        button_ok = self.widget_creator.create_button("Aceptar", "ok", self.accept)

        button_box = QtWidgets.QHBoxLayout()
        button_box.addWidget(button_add)
        button_box.addWidget(button_remove)
        button_box.addWidget(button_ok)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_box)

        self.setLayout(self.layout)
        self.show()

    def cellChanged(self, row, column):
        CATEGORY_COLUMN = 0
        COMMENT_COLUMN = 1
        FLAG_COLUMNS = {
            2: 'income',
            3: 'not_computed'
        }

        if column in FLAG_COLUMNS:
            category = self.table.item(row, CATEGORY_COLUMN).text()
            value = self.table.item(row, column).checkState() == Qt.CheckState.Checked

            self.expense_types_service.update_expense_type_flag(category, FLAG_COLUMNS[column], value)
            return

        if column == CATEGORY_COLUMN:
            old_category = self.previous_value
            old_comment = self.table.item(row, COMMENT_COLUMN).text()

            field = 'category'
            new_value = self.table.item(row, CATEGORY_COLUMN).text()
        elif column == COMMENT_COLUMN:
            old_category = self.table.item(row, CATEGORY_COLUMN).text()
            old_comment = self.previous_value

            field = 'comment'
            new_value = self.table.item(row, COMMENT_COLUMN).text()

        self.expense_types_service.update_expense_type(old_category, old_comment, field, new_value)

        if field == 'category':
            self.refresh_categories()

    def cellClicked(self, row, column):
        self.previous_value = self.table.item(row, column).text()

    def add_category(self):
        add_category_dialog = AddCategoryDialog(self)

    def add_category_to_table(self, category_name, category_description, income, not_computed):
        # Same order as the categories come from the database (ORDER BY category)
        row = 0

        while row < self.table.rowCount() and self.table.item(row, 0).text() < category_name:
            row += 1

        # Avoid cellChanged updating the database while the row is filled
        self.table.blockSignals(True)

        self.table.insertRow(row)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(category_name))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(category_description))
        self.table.setItem(row, 2, self.widget_creator.create_checkbox_item(income))
        self.table.setItem(row, 3, self.widget_creator.create_checkbox_item(not_computed))

        self.table.blockSignals(False)

        self.table.resizeColumnsToContents()
        self.table.selectRow(row)

        self.refresh_categories()

    def remove_selected_rows(self):
        # selectedIndexes returns one index per cell, so a row can appear more than once
        indexes = list(set(map(lambda x: x.row(), self.table.selectedIndexes())))
        indexes.sort(reverse=True)

        for i in indexes:
            category_text = self.table.item(i, 0).text()

            self.table.removeRow(i)
            self.expense_types_service.remove_category(category_text)

        self.refresh_categories()

    def refresh_categories(self):
        # Update the categories combobox of the classification screen
        self.listeners_pool.send_event('classificator', 'refresh_categories')
        self.listeners_pool.send_event('search-filter', 'refresh_categories')
