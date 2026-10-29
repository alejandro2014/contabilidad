from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QCompleter, QGroupBox, QVBoxLayout, QWidget

from src.dialogs.ErrorDialog import ErrorDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.events.ListenerNode import ListenerNode

from src.services.ComboBoxService import ComboBoxService

class Classifier(QWidget, ListenerNode):
    def __init__(self, listeners_pool, show_classify_button, *args, **kwargs):
        super(Classifier, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'classificator', listeners_pool)

        widget_creator = WidgetCreator()

        self.categories = widget_creator.create_categories_combobox()
        self.classify_button = widget_creator.create_button('Clasificar elementos', 'ok', self.classify_elements)

        if show_classify_button:
            self.init_type_ahead()

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

    def init_type_ahead(self):
        # Typing part of a type shows the ones that contain it, and Enter classifies with it
        self.categories.setEditable(True)
        self.categories.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.categories.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.categories.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.categories.lineEdit().returnPressed.connect(self.classify_elements)

    def type_ahead(self, text):
        # The pending table sends here what is typed on it
        self.categories.setFocus()
        self.categories.lineEdit().setText(text)

        completer = self.categories.completer()
        completer.setCompletionPrefix(text)
        completer.complete()

    def refresh_categories(self):
        current_category = self.categories.currentText()

        self.categories.clear()
        self.categories.addItems(ComboBoxService().get_categories())

        # Keep the selected category if it still exists
        index = self.categories.findText(current_category)

        if index >= 0:
            self.categories.setCurrentIndex(index)

    def selected_category(self):
        # The typed text may differ in case from the type, or not be a type at all
        index = self.categories.findText(self.categories.currentText().strip(), Qt.MatchFlag.MatchFixedString)

        return None if index < 0 else self.categories.itemText(index)

    def classify_elements(self):
        category = self.selected_category()

        if category is None:
            ErrorDialog(self, title = 'Error: Tipo de gasto desconocido', message = f'No hay ningún tipo de gasto "{self.categories.currentText()}"')
            return

        self.categories.setCurrentText(category)

        self.send_event('pending-expenses-table', 'classify_selected', data = category)
        self.send_event('status-bar', 'refresh')
