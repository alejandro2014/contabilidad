from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout


class BaseDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)

    def init_widgets(self, widgets, layout="vertical"):
        self.layout = QVBoxLayout(self) if layout == "vertical" else QHBoxLayout(self)

        for widget in widgets:
            self.layout.addWidget(widget)