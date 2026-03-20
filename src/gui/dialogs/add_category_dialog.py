from src.gui.dialogs.ErrorDialog import ErrorDialog
from src.gui.dialogs.base_dialog import BaseDialog

from src.services.categories_service import CategoriesService

from src.gui.widgets.input_text import InputText
from src.gui.widgets.button_box import ButtonBox


class AddCategoryDialog(BaseDialog):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)

        self.categories_service = CategoriesService()
    
        self.init_dialog(
            title = "Añadir categoría",
            layout = "vertical", 
            widgets = [
                InputText('Nombre'),
                InputText('Descripción'),
                ButtonBox(self, id='cancel-accept-add-category-dialog')
            ]
        )

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
