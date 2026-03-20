from PySide6.QtWidgets import QComboBox, QLabel, QHBoxLayout, QWidget


class ComboBox(QWidget):
    def __init__(self, title, combobox_service=None):
        super().__init__()

        self.title = title
        self.service = combobox_service

        label = QLabel(self.title + ':')
        self.combo = QComboBox()
        label.setBuddy(self.combo)

        layout = QHBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.combo)

        self.refresh_values()
    
    def refresh_values(self):
        values = self.service.get_values()
        self.combo.clear()
        self.combo.insertItems(0, values)
