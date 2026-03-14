from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit

from src.gui.dialogs.WidgetCreator import WidgetCreator
from src.gui.dialogs.ErrorDialog import ErrorDialog

from src.services.categories_service import CategoriesService

class AddCategoryDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(AddCategoryDialog, self).__init__(self.parent)

        self.widget_creator = WidgetCreator()

        self.setWindowTitle("Añadir categoría")
        self.resize(500, 300)
        self.setModal(True)

        name_layout = QHBoxLayout()

        name_label = QLabel("Nombre:")
        self.name_textbox = QLineEdit()
        name_label.setBuddy(self.name_textbox)

        description_layout = QHBoxLayout()

        description_label = QLabel("Descripción:")
        self.description_textbox = QLineEdit()
        description_label.setBuddy(self.description_textbox)

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_textbox)

        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_textbox)

        button_cancel = self.widget_creator.create_button("Cancelar", "cancel", self.reject)
        button_ok = self.widget_creator.create_button("Aceptar", "ok", self.check_category)

        button_box = QHBoxLayout()
        button_box.addWidget(button_cancel)
        button_box.addWidget(button_ok)

        self.layout = QVBoxLayout()
        self.layout.addLayout(name_layout)
        self.layout.addLayout(description_layout)
        self.layout.addLayout(button_box)

        self.setLayout(self.layout)
        self.show()

        self.categories_service = CategoriesService()

    def check_category(self):
        category_name = self.name_textbox.text()
        category_description = self.description_textbox.text()

        if category_name == '':
            ErrorDialog(self, title = "Error: Nombre vacío", message = "El nombre de la categoría no puede estar vacío")
            return

        category_exists = self.categories_service.category_exists(category_name)

        if category_exists:
            ErrorDialog(self, title = "Error: La categoría ya existe", message = f'Ya se ha introducido una categoría "{category_name}"')
            return

        self.accept()

        return category_name, category_description
    
    def get_data(self):
        return [
            self.name_textbox.text(),
            self.description_textbox.text()
        ]
