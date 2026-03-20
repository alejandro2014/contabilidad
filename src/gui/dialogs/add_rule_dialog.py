from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit

from src.gui.dialogs.ErrorDialog import ErrorDialog
from src.gui.widgets.combobox import ComboBox
from src.gui.widgets.input_text import InputText

from src.gui.widgets.combobox_services.categories_combobox_service import CategoriesComboboxService

from src.gui.widgets.button_box import ButtonBox


class AddRuleDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(AddRuleDialog, self).__init__(self.parent)

        self.categories_service = CategoriesComboboxService()

        self.setWindowTitle("Añadir regla")
        self.setModal(True)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(ComboBox('Categoría', self.categories_service))
        self.layout.addWidget(InputText('Expresión'))
        self.layout.addWidget(ButtonBox(self, id='cancel-accept'))

        self.show()

    def add_rule(self):
        pass
    
