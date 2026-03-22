from PySide6.QtWidgets import QLabel

from src.gui.dialogs.base_dialog import BaseDialog
from src.gui.widgets.button_box import ButtonBox


class ErrorDialog(BaseDialog):
    def __init__(self, parent, title="Error", message="Unknown error"):
        self.parent = parent
        super().__init__(self.parent)
    
        self.init_dialog(
            title=title,
            layout = "vertical", 
            widgets = [
                QLabel(message),
                ButtonBox(self, id='accept')
            ]
        )
