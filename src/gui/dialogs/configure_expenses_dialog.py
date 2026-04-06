from PySide6 import QtWidgets
from PySide6.QtWidgets import QAbstractItemView, QDialog, QTableWidget, QTableWidgetItem

from src.config.ConfigLoader import ConfigLoader

from src.gui.dialogs.add_category_dialog import AddCategoryDialog

from src.services.categories_service import CategoriesService

from src.gui.widgets.pictured_button import PicturedButton
from src.gui.widgets.button_box import ButtonBox

from src.gui.widgets.table import Table

from src.gui.dialogs.ErrorDialog import ErrorDialog


class ConfigureExpensesDialog(QDialog):
    def __init__(self, parent):
        super(ConfigureExpensesDialog, self).__init__(parent)

        self.service = CategoriesService()
        self.table_id = 'expense-types'

        self.table = Table('expense-types',
                           service=self.service,
                           get_method='get_categories',
                           delete_method='delete_categories')

        self.setWindowTitle("Configuración de categorías")
        self.resize(600, 400)
        self.setModal(True)

        button_box = QtWidgets.QHBoxLayout()
        button_box.addWidget(PicturedButton("Añadir categoría", "upload", self.add_category))
        button_box.addWidget(PicturedButton("Eliminar seleccionadas", "bin", self.table.remove_selected_rows))
        button_box.addWidget(PicturedButton("Aceptar", "ok", self.accept))

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_box)

        self.setLayout(self.layout)
        self.show()

        self.table.refresh()
    
    def add_category(self):
        dialog = AddCategoryDialog(self)

        if dialog.exec() == QDialog.Accepted and self.is_category_ok(dialog):
            name, description = dialog.get_data()
            self.service.add_category(name, description)
            self.table.refresh()

    def is_category_ok(self, dialog):
        category_name = dialog.get_name()
        
        if category_name == '':
            ErrorDialog(self, title="Error: Nombre vacío", message="El nombre de la categoría no puede estar vacío")
            return False

        category_exists = self.service.category_exists(category_name)

        if category_exists:
            ErrorDialog(self, title="Error: La categoría ya existe", message=f'Ya se ha introducido una categoría "{category_name}"')
            return False

        return True
