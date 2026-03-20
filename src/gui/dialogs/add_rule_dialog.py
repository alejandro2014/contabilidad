from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit

from src.gui.dialogs.ErrorDialog import ErrorDialog
from src.gui.widgets.combobox import ComboBox

from src.gui.widgets.combobox_services.categories_combobox_service import CategoriesComboboxService

from src.gui.widgets.button_box import ButtonBox


class AddRuleDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super(AddRuleDialog, self).__init__(self.parent)

        self.categories_service = CategoriesComboboxService()

        self.setWindowTitle("Añadir regla")
        self.setModal(True)
        
        description_label = QLabel("Expresión:")
        self.description_textbox = QLineEdit()
        description_label.setBuddy(self.description_textbox)

        description_layout = QHBoxLayout()
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_textbox)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(ComboBox('Categoría', self.categories_service))
        self.layout.addLayout(description_layout)
        self.layout.addWidget(ButtonBox(self, id='cancel-accept'))

        self.show()

    def add_rule(self):
        pass
    
