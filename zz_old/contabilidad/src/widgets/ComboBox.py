from PySide2.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget

from src.services.ComboBoxService import ComboBoxService

from globals import widgets_pool as wpool

from src.widgets.RootWidget import RootWidget

class ComboBox(RootWidget):
    def __init__(self, title="", method="", service=None):
        super().__init__()

        self.title = title
        self.service = service
        self.method = method
        self.combo = QComboBox()

    def create_layout(self):
        layout = QHBoxLayout()

        if self.title != "":
            layout.addWidget(QLabel(f'{self.title}:'))

        layout.addWidget(self.combo)

        self.setLayout(layout)

    def init_widgets(self):
        if self.method == "":
            return

        if self.service is None:
            self.service = ComboBoxService()

        values = getattr(self.service, self.method)()

        for value in values:
            self.combo.addItem(value)
