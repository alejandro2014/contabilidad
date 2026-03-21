from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit

from src.gui.dialogs.ErrorDialog import ErrorDialog

from src.gui.widgets.combobox import ComboBox
from src.gui.widgets.input_text import InputText
from src.gui.widgets.button_box import ButtonBox

from src.services.combobox_services.categories_combobox_service import CategoriesComboboxService

from src.gui.dialogs.base_dialog import BaseDialog


class AddRuleDialog(BaseDialog):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)

        self.categories_service = CategoriesComboboxService()

        self.init_dialog(
            title = "Añadir regla",
            layout = "vertical", 
            widgets = [
                ComboBox('Categoría', self.categories_service),
                InputText('Expresión'),
                ButtonBox(self, id='cancel-accept')
            ]
        )

    def accept(self):
        self.add_rule()

    def add_rule(self):
        pass
    
