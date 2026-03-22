from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget


class InputText(QWidget):
    def __init__(self, text=None):
        super().__init__()

        label = QLabel(f'{text}:')
        self.textbox = QLineEdit()
        label.setBuddy(self.textbox)

        layout = QHBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.textbox)

    def get_text(self):
        return self.textbox.text()