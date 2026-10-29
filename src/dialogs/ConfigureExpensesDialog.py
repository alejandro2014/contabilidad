from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QInputDialog, QMessageBox

from src.config.ConfigLoader import ConfigLoader

from src.dialogs.AddCategoryDialog import AddCategoryDialog
from src.dialogs.ErrorDialog import ErrorDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.ExpenseTypesService import ExpenseTypesService
from src.services.LoadFileService import LoadFileService

class ConfigureExpensesDialog(QDialog):
    CATEGORY_COLUMN = 0
    COMMENT_COLUMN = 1
    FLAG_COLUMNS = {
        2: 'income',
        3: 'not_computed'
    }

    LEAVE_PENDING = "Dejar los movimientos pendientes y borrar sus reglas"

    def __init__(self, parent, listeners_pool):
        super(ConfigureExpensesDialog, self).__init__(parent)

        self.listeners_pool = listeners_pool

        self.widget_creator = WidgetCreator()
        self.usecases_service = LoadFileService()
        self.expense_types_service = ExpenseTypesService()

        self.setWindowTitle("Configuración de categorías")
        self.resize(600, 400)
        self.setModal(True)

        table_info = ConfigLoader().load_table('expense-types')

        expense_types = self.expense_types_service.select_expense_types_full()

        self.table = self.widget_creator.create_table(table_info, expense_types)

        for row in range(self.table.rowCount()):
            self.save_category_name(row)

        self.table.cellChanged.connect(self.cellChanged)

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

    def save_category_name(self, row):
        # The name stored in the database, to know which type is renamed after its cell is edited
        item = self.table.item(row, self.CATEGORY_COLUMN)
        item.setData(Qt.ItemDataRole.UserRole, item.text())

    def cellChanged(self, row, column):
        category_item = self.table.item(row, self.CATEGORY_COLUMN)
        category = category_item.data(Qt.ItemDataRole.UserRole)

        if column in self.FLAG_COLUMNS:
            value = self.table.item(row, column).checkState() == Qt.CheckState.Checked

            self.expense_types_service.update_expense_type_flag(category, self.FLAG_COLUMNS[column], value)
        elif column == self.COMMENT_COLUMN:
            self.expense_types_service.update_comment(category, self.table.item(row, column).text())
        elif column == self.CATEGORY_COLUMN:
            self.rename_category(row, category, category_item.text().strip())

    def rename_category(self, row, old_category, new_category):
        if new_category == old_category:
            return

        error = None

        if new_category == '':
            error = ("Error: Nombre vacío", "El nombre de la categoría no puede estar vacío")
        elif self.expense_types_service.check_category_exists(new_category):
            error = ("Error: La categoría ya existe", f'Ya se ha introducido una categoría "{new_category}"')

        if error is not None:
            self.set_category_text(row, old_category)
            ErrorDialog(self, title = error[0], message = error[1])
            return

        self.expense_types_service.rename_category(old_category, new_category)

        self.set_category_text(row, new_category)
        self.save_category_name(row)
        self.refresh_categories()

    def set_category_text(self, row, text):
        # Without cellChanged saving it again
        self.table.blockSignals(True)
        self.table.item(row, self.CATEGORY_COLUMN).setText(text)
        self.table.blockSignals(False)

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
        self.save_category_name(row)

        self.table.blockSignals(False)

        self.table.resizeColumnsToContents()
        self.table.selectRow(row)

        self.refresh_categories()

    def remove_selected_rows(self):
        # selectedIndexes returns one index per cell, so a row can appear more than once
        rows = sorted(set(map(lambda x: x.row(), self.table.selectedIndexes())), reverse=True)
        selected_categories = [ self.table.item(row, self.CATEGORY_COLUMN).data(Qt.ItemDataRole.UserRole) for row in rows ]

        # The expenses can't be moved to a type that is also being deleted
        other_categories = [ c for c in self.expense_types_service.get_categories_simple() if c not in selected_categories ]

        for row, category in zip(rows, selected_categories):
            confirmed, new_category = self.ask_remove_category(category, other_categories)

            if not confirmed:
                continue

            self.expense_types_service.remove_category(category, new_category)
            self.table.removeRow(row)

        self.refresh_categories()
        self.listeners_pool.send_event('pending-expenses-table', 'refresh_rows')
        self.listeners_pool.send_event('status-bar', 'refresh')

    def ask_remove_category(self, category, other_categories):
        # Returns whether to delete it, and the type its expenses and rules go to (None: pending again)
        title = "Eliminar categoría"
        expenses_count, rules_count = self.expense_types_service.get_category_usage(category)

        if expenses_count == 0 and rules_count == 0:
            answer = QMessageBox.question(self, title, f'¿Eliminar la categoría "{category}"?')

            return answer == QMessageBox.StandardButton.Yes, None

        message = f'"{category}" tiene {expenses_count} movimientos y {rules_count} reglas.\n¿Qué hacer con ellos?'
        options = [ self.LEAVE_PENDING ] + [ f'Pasarlos a "{c}"' for c in other_categories ]

        choice, ok = QInputDialog.getItem(self, title, message, options, 0, False)

        if not ok:
            return False, None

        index = options.index(choice)

        return True, None if index == 0 else other_categories[index - 1]

    def refresh_categories(self):
        # Update the categories combobox of the classification screen
        self.listeners_pool.send_event('classificator', 'refresh_categories')
        self.listeners_pool.send_event('search-filter', 'refresh_categories')
