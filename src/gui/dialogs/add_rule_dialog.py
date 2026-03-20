from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit

from src.gui.dialogs.WidgetCreator import WidgetCreator
from src.gui.dialogs.ErrorDialog import ErrorDialog
from src.gui.widgets.combobox import ComboBox

from src.gui.widgets.combobox_services.categories_combobox_service import CategoriesComboboxService
from src.gui.widgets.pictured_button import PicturedButton

from src.config.ConfigLoader import ConfigLoader


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

        buttons_info = ConfigLoader().load_buttons('cancel-accept')

        button_box = QHBoxLayout()
        for button_info in buttons_info:
            button_box.addWidget(PicturedButton(text=button_info['text'], image=button_info['image'], action=getattr(self, button_info['action'])))

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(combo_categories)
        self.layout.addLayout(description_layout)
        self.layout.addLayout(button_box)

        self.show()

    def add_rule(self):
        pass
    
