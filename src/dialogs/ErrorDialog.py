from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel
from src.dialogs.WidgetCreator import WidgetCreator

class ErrorDialog(QDialog):
    def __init__(self, parent, title="Error", message=""):
        super(ErrorDialog, self).__init__(parent)

        self.setWindowTitle(title)
        self.resize(200, 200)
        self.setModal(True)

        widget_creator = WidgetCreator()

        label = QLabel(message)
        button_accept = widget_creator.create_button("Aceptar", "ok", self.accept)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(label)
        layout.addWidget(button_accept)

        self.show()
