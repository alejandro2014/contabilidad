from PySide2.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from src.services.ExpenseTypesService import ExpenseTypesService
from src.services.PendingExpensesService import PendingExpensesService

from src.widgets.BaseWidget import BaseWidget

from globals import widgets_pool as wpool

class Classifier(QWidget, BaseWidget):
    # TODO Can the show_classify_button be removed?
    def __init__(self, show_classify_button, *args, **kwargs):
        super(Classifier, self).__init__(*args, **kwargs)

        self.show_classify_button = show_classify_button

        self.expense_types_service = ExpenseTypesService()
        self.expenses_service = PendingExpensesService()

        self.categories = self.create_combobox('get_category_names', service=self.expense_types_service)
        self.classify_button = self.create_button('Clasificar elementos', 'ok', self.classify_elements)

    def get_widgets_from_pool(self):
        pass

    def init_widgets(self):
        pass

    def create_layout(self):
        layout = QVBoxLayout()

        self.inner_layout = QVBoxLayout()
        self.inner_layout.addWidget(self.categories)

        if self.show_classify_button:
            self.inner_layout.addWidget(self.classify_button)

        group_box_title = 'Clasificar por tipo' if self.show_classify_button else 'Tipo de gasto'

        group_box = QGroupBox(group_box_title)
        group_box.setLayout(self.inner_layout)

        layout.addWidget(group_box)

        self.setLayout(layout)

    def classify_elements(self):
        category = self.categories.currentText()
        expenses = wpool.execute('pending-expenses-table', 'get_current_expenses')

        self.expenses_service.classify_expenses(expenses, category)

        wpool.execute('pending-expenses-table', 'refresh')
        wpool.execute('menubar', 'refresh')

    def refresh(self):
        self.inner_layout.removeWidget(self.categories)
        self.categories = self.create_combobox('get_category_names', service=self.expense_types_service)

        self.inner_layout.addWidget(self.categories)

        if self.show_classify_button:
            self.inner_layout.addWidget(self.classify_button)
