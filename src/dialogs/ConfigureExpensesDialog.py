from PySide2 import QtWidgets, QtGui
from PySide2.QtWidgets import QDialog

from src.config.ConfigLoader import ConfigLoader

from src.dialogs.AddCategoryDialog import AddCategoryDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.ExpenseTypesService import ExpenseTypesService
from src.services.UseCasesService import UseCasesService

class ConfigureExpensesDialog(QDialog):
    def __init__(self, parent):
        super(ConfigureExpensesDialog, self).__init__(parent)

        self.widget_creator = WidgetCreator()
        self.usecases_service = UseCasesService()
        self.expense_types_service = ExpenseTypesService()

        self.setWindowTitle("Configuración de categorías")
        self.resize(600, 400)
        self.setModal(True)

        table_info = ConfigLoader().load_table('expense-types')

        expense_types = self.expense_types_service.select_expense_types_full()

        self.table = self.widget_creator.create_table(table_info, expense_types)

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
