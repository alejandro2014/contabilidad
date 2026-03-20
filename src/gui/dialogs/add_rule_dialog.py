from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit

from src.gui.dialogs.WidgetCreator import WidgetCreator
from src.gui.dialogs.ErrorDialog import ErrorDialog
from src.gui.widgets.combobox import ComboBox

from src.gui.widgets.combobox_services.categories_combobox_service import CategoriesComboboxService


class AddRuleDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(AddRuleDialog, self).__init__(self.parent)

        self.categories_service = CategoriesComboboxService()

        self.widget_creator = WidgetCreator()

        self.setWindowTitle("Añadir regla")
        self.resize(500, 300)
        self.setModal(True)

        combo_categories = ComboBox('Categoría', self.categories_service)
        
        description_label = QLabel("Expresión:")
        self.description_textbox = QLineEdit()
        description_label.setBuddy(self.description_textbox)

        description_layout = QHBoxLayout()
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_textbox)

        button_cancel = self.widget_creator.create_button("Cancelar", "cancel", self.reject)
        button_ok = self.widget_creator.create_button("Aceptar", "ok", self.check_category)

        button_box = QHBoxLayout()
        button_box.addWidget(button_cancel)
        button_box.addWidget(button_ok)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(combo_categories)
        self.layout.addLayout(description_layout)
        self.layout.addLayout(button_box)

        self.show()

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
