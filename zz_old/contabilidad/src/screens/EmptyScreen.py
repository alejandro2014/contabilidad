from PySide2.QtWidgets import QLabel, QVBoxLayout, QWidget
from src.widgets.RootWidget import RootWidget

class EmptyScreen(RootWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("No hay gastos clasificados. Cargue un fichero de gastos y clasifíquelos")

    def create_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.label)

        self.setLayout(layout)

    def init_widgets(self):
        pass
