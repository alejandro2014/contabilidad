from PySide2 import QtWidgets, QtGui
from PySide2.QtWidgets import QDialog

from src.config.ConfigLoader import ConfigLoader

from src.dialogs.AddCategoryDialog import AddCategoryDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.ExpenseTypesService import ExpenseTypesService
from src.services.LoadFileService import LoadFileService

class ConfigureExpensesDialog(QDialog):
    def __init__(self, parent):
        super(ConfigureExpensesDialog, self).__init__(parent)

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

    def cellClicked(self, row, column):
        self.previous_value = self.table.item(row, column).text()

    def add_category(self):
        add_category_dialog = AddCategoryDialog(self)

    def add_category_to_table(self, category_name, category_description):
        #TODO Refresh this into the table
        #TODO Insert the row in the correct order
        pass

    def remove_selected_rows(self):
        indexes = list(map(lambda x: x.row(), self.table.selectedIndexes()))
        indexes.sort(reverse=True)

        for i in indexes:
            category_text = self.table.item(i, 0).text()

            self.table.removeRow(i)
            self.expense_types_service.remove_category(category_text)
