from src.gui.dialogs.base_dialog import BaseDialog

from src.services.categories_service import CategoriesService

from src.gui.widgets.input_text import InputText
from src.gui.widgets.button_box import ButtonBox


class AddCategoryDialog(BaseDialog):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)

        self.categories_service = CategoriesService()
    
        self.name_textbox = InputText('Nombre')
        self.description_textbox = InputText('Descripción')
        
        self.init_dialog(
            title = "Añadir categoría",
            layout = "vertical", 
            widgets = [
                self.name_textbox,
                self.description_textbox,
                ButtonBox(self, id='cancel-accept')
            ]
        )
    
    def get_data(self):
        return [
            self.name_textbox.get_text(),
            self.description_textbox.get_text()
        ]
    
    def get_name(self):
        return self.name_textbox.get_text()
    
    def get_description(self):
        return self.description_textbox.get_text()
