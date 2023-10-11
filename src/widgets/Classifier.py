from PySide2.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from src.dialogs.WidgetCreator import WidgetCreator

from src.events.ListenerNode import ListenerNode

from src.services.ComboBoxService import ComboBoxService
from src.services.PendingExpensesService import PendingExpensesService

class Classifier(QWidget, ListenerNode):
    def __init__(self, listeners_pool, show_classify_button, *args, **kwargs):
        super(Classifier, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'classificator', listeners_pool)

        self.combo_service = ComboBoxService()
        self.expenses_service = PendingExpensesService()

        widget_creator = WidgetCreator()

        self.categories = widget_creator.create_combobox(self.combo_service, 'get_categories')
        self.classify_button = widget_creator.create_button('Clasificar elementos', 'ok', self.classify_elements)

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
        expenses = self.send_event('pending-expenses-table', 'get_current_expenses')

        print('================')
        print(expenses)
        self.expenses_service.classify_expenses(expenses, category)

        self.send_event('pending-expenses-table', 'refresh_rows')
