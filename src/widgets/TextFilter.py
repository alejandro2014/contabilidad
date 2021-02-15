from PySide2.QtWidgets import QGroupBox, QLineEdit, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

class TextFilter(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(TextFilter, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'text-filter', listeners_pool)

        self.line_edit = QLineEdit()

        layout = QVBoxLayout()
        self.setLayout(layout)

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.line_edit)

        group_box = QGroupBox("Texto a buscar")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.line_edit.textEdited.connect(self.text_changed)

    def text_changed(self, text):
        value = None

        if len(text) > 1:
            value = text

        self.send_event('filter-widget', 'change_search_value', value)
