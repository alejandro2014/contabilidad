from PySide2.QtWidgets import QGroupBox, QLineEdit, QVBoxLayout, QWidget

from globals import widgets_pool as wpool

from src.widgets.RootWidget import RootWidget

class TextFilter(RootWidget):
    def __init__(self):
        super().__init__()

        self.line_edit = QLineEdit()
        self.line_edit.textEdited.connect(self.text_changed)

        self.widget_ids = [ 'line-edit' ]

    def create_layout(self):
        layout = QVBoxLayout()

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.line_edit)

        group_box = QGroupBox("Texto a buscar")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.setLayout(layout)

    def text_changed(self, text):
        if len(text) < 2:
            return

        wpool.execute('filter-widget', 'change_search_value', text)
