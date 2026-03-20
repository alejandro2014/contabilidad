from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout


class BaseDialog(QDialog):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)

    def init_dialog(self, title=None, layout=None, widgets=None):
        self.setWindowTitle(title)
        self.setModal(True)
        self.init_widgets(widgets, layout)
        self.show()

    def init_widgets(self, widgets, layout=None):
        self.layout = QVBoxLayout(self) if layout == "vertical" else QHBoxLayout(self)

        for widget in widgets:
            self.layout.addWidget(widget)