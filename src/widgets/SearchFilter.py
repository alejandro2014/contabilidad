import math

from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

from src.services.ComboBoxService import ComboBoxService

class SearchFilter(QWidget, ListenerNode):
    ALL_CATEGORIES = 'Todos los tipos'

    def __init__(self, listeners_pool, show_categories, *args, **kwargs):
        super(SearchFilter, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'search-filter', listeners_pool)

        self.show_categories = show_categories

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText('Parte del concepto')

        self.amount_from = self.create_amount_edit('Mínimo')
        self.amount_to = self.create_amount_edit('Máximo')

        self.categories = QComboBox()

        self.clear_button = QPushButton('Limpiar')
        self.clear_button.clicked.connect(self.clear)

        layout = QVBoxLayout()
        self.setLayout(layout)

        concept_layout = QHBoxLayout()
        concept_layout.addWidget(QLabel('Concepto:'))
        concept_layout.addWidget(self.line_edit)

        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel('Importe:'))
        amount_layout.addWidget(self.amount_from)
        amount_layout.addWidget(QLabel('-'))
        amount_layout.addWidget(self.amount_to)

        inner_layout = QVBoxLayout()
        inner_layout.addLayout(concept_layout)
        inner_layout.addLayout(amount_layout)

        # Only the classified expenses have a type
        if show_categories:
            category_layout = QHBoxLayout()
            category_layout.addWidget(QLabel('Tipo:'))
            category_layout.addWidget(self.categories)
            inner_layout.addLayout(category_layout)

            self.refresh_categories()

        inner_layout.addWidget(self.clear_button)

        group_box = QGroupBox("Buscar")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.line_edit.textEdited.connect(self.search_changed)
        self.amount_from.textEdited.connect(self.search_changed)
        self.amount_to.textEdited.connect(self.search_changed)
        self.categories.currentIndexChanged.connect(self.search_changed)

    def create_amount_edit(self, placeholder):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)

        return line_edit

    def refresh_categories(self):
        current_category = self.categories.currentText()

        # Filling the combo must not launch a search for every item
        self.categories.blockSignals(True)

        self.categories.clear()
        self.categories.addItem(self.ALL_CATEGORIES)
        self.categories.addItems(ComboBoxService().get_categories())

        # Keep the selected category if it still exists
        self.categories.setCurrentIndex(max(self.categories.findText(current_category), 0))

        self.categories.blockSignals(False)

    def search_changed(self, value = None):
        self.send_event('filter-widget', 'change_search', self.get_search())

    def get_search(self):
        text = self.line_edit.text()
        category = self.categories.currentText()

        return {
            'search_value': text if len(text) > 1 else None,
            'amount': {
                'from': self.parse_amount(self.amount_from.text()),
                'to': self.parse_amount(self.amount_to.text())
            },
            'category': category if self.show_categories and category != self.ALL_CATEGORIES else None
        }

    def parse_amount(self, text):
        # The amounts can be typed with a decimal comma, and an amount not finished yet is ignored
        try:
            amount = abs(float(text.strip().replace(',', '.')))
        except ValueError:
            return None

        return amount if math.isfinite(amount) else None

    def clear(self):
        self.line_edit.clear()
        self.amount_from.clear()
        self.amount_to.clear()

        self.categories.blockSignals(True)
        self.categories.setCurrentIndex(0)
        self.categories.blockSignals(False)

        self.search_changed()
