from PySide6.QtWidgets import QComboBox, QLabel, QHBoxLayout, QWidget


class ComboBox(QWidget):
    def __init__(self, title=None, combobox_service=None):
        super().__init__()

        self.title = title
        self.service = combobox_service

        self.combo = QComboBox()

        layout = QHBoxLayout(self)

        if title is not None:
            label = QLabel(self.title + ':')
            label.setBuddy(self.combo)
            layout.addWidget(label)
            
        layout.addWidget(self.combo)

        self.refresh_values()
    
    def refresh_values(self):
        values = self.service.get_values()
        self.combo.clear()
        self.combo.insertItems(0, values)
