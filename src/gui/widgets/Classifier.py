from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

from src.services.combobox_services.categories_combobox_service import CategoriesComboboxService

from src.gui.widgets.combobox import ComboBox
from src.gui.widgets.pictured_button import PicturedButton


class Classifier(QWidget, ListenerNode):
    def __init__(self, listeners_pool, show_classify_button, *args, **kwargs):
        super(Classifier, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'classificator', listeners_pool)


        self.categories = ComboBox('Categoría', CategoriesComboboxService())
        self.classify_button = PicturedButton('Clasificar elementos', 'ok', self.classify_elements)

        layout = QVBoxLayout()
        self.setLayout(layout)

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.categories)

        if show_classify_button:
            inner_layout.addWidget(self.classify_button)

        group_box_title = 'Clasificar por tipo' if show_classify_button else 'Tipo de gasto'

        group_box = QGroupBox(group_box_title)
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

    def classify_elements(self):
        category = self.categories.currentText()

        self.send_event('pending-expenses-table', 'classify_selected', data = category)
        self.send_event('status-bar', 'refresh')