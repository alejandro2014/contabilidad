from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon

class PicturedButton(QPushButton):
    def __init__(self, text=None, image=None, action=None):
        super().__init__()

        self.pictures_path = "src/config/images"

        self.setText(text)
        self.setIcon(QIcon(f"{self.pictures_path}/{image}.png"))
        self.clicked.connect(action)