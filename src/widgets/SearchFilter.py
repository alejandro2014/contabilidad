import math

from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

from src.services.ComboBoxService import ComboBoxService

class SearchFilter(QWidget, ListenerNode):
    ALL_CATEGORIES = 'Todos los tipos'
    ALL_TAGS = 'Todas las etiquetas'

    def __init__(self, listeners_pool, show_categories, *args, **kwargs):
        super(SearchFilter, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'search-filter', listeners_pool)

        self.show_categories = show_categories

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText('Parte del concepto')

        self.amount_from = self.create_amount_edit('Mínimo')
        self.amount_to = self.create_amount_edit('Máximo')

        self.categories = QComboBox()
        self.tags = QComboBox()

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

            # The tags are only given to classified expenses too
            tag_layout = QHBoxLayout()
            tag_layout.addWidget(QLabel('Etiqueta:'))
            tag_layout.addWidget(self.tags)
            inner_layout.addLayout(tag_layout)

            self.refresh_tags()

        inner_layout.addWidget(self.clear_button)

        group_box = QGroupBox("Buscar")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.line_edit.textEdited.connect(self.search_changed)
        self.amount_from.textEdited.connect(self.search_changed)
        self.amount_to.textEdited.connect(self.search_changed)
        self.categories.currentIndexChanged.connect(self.search_changed)
        self.tags.currentIndexChanged.connect(self.search_changed)

    def create_amount_edit(self, placeholder):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)

        return line_edit

    def refresh_categories(self):
        self.refresh_combo(self.categories, self.ALL_CATEGORIES, ComboBoxService().get_categories())

    def refresh_tags(self):
        self.refresh_combo(self.tags, self.ALL_TAGS, ComboBoxService().get_tags())

    def refresh_combo(self, combo, all_text, values):
        current_value = combo.currentText()

        # Filling the combo must not launch a search for every item
        combo.blockSignals(True)

        combo.clear()
        combo.addItem(all_text)
        combo.addItems(values)

        # Keep the selected value if it still exists
        combo.setCurrentIndex(max(combo.findText(current_value), 0))

        combo.blockSignals(False)

    def set_search(self, search_value=None, category=None, tag=None):
        # Shows a search chosen somewhere else (a chart of the dashboard) without searching for every field
        for widget in [ self.line_edit, self.amount_from, self.amount_to, self.categories, self.tags ]:
            widget.blockSignals(True)

        self.line_edit.setText(search_value or '')
        self.amount_from.clear()
        self.amount_to.clear()
        self.categories.setCurrentIndex(max(self.categories.findText(category or self.ALL_CATEGORIES), 0))
        self.tags.setCurrentIndex(max(self.tags.findText(tag or self.ALL_TAGS), 0))

        for widget in [ self.line_edit, self.amount_from, self.amount_to, self.categories, self.tags ]:
            widget.blockSignals(False)

    def search_changed(self, value = None):
        self.send_event('filter-widget', 'change_search', self.get_search())

    def get_search(self):
        text = self.line_edit.text()
        category = self.categories.currentText()
        tag = self.tags.currentText()

        return {
            'search_value': text if len(text) > 1 else None,
            'amount': {
                'from': self.parse_amount(self.amount_from.text()),
                'to': self.parse_amount(self.amount_to.text())
            },
            'category': category if self.show_categories and category != self.ALL_CATEGORIES else None,
            'tag': tag if self.show_categories and tag != self.ALL_TAGS else None
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

        for combo in [ self.categories, self.tags ]:
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.blockSignals(False)

        self.search_changed()
