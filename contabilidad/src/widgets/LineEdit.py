from PySide2.QtWidgets import QLabel, QHBoxLayout, QLineEdit, QWidget

from globals import widgets_pool as wpool

from src.widgets.RootWidget import RootWidget

class LineEdit(RootWidget):
    def __init__(self, text):
        super().__init__()

        self.label = QLabel(text)
        self.line_edit = QLineEdit()
        self.label.setBuddy(self.line_edit)

        self.create_layout()

    def create_layout(self):
        layout = QHBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)

        self.setLayout(layout)

    def setText(self, text):
        self.line_edit.setText(text)
