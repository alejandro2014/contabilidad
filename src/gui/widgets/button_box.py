from PySide6.QtWidgets import QHBoxLayout, QWidget
from src.config.ConfigLoader import ConfigLoader

from src.gui.widgets.pictured_button import PicturedButton


class ButtonBox(QWidget):
    def __init__(self, parent, id=None):
        super().__init__()

        buttons_info = ConfigLoader().load_buttons(id)

        button_box = QHBoxLayout(self)

        for button_info in buttons_info:
            button_box.addWidget(
                PicturedButton(
                    text=button_info['text'], 
                    image=button_info['image'], 
                    action=getattr(parent, button_info['action'])
                )
            )