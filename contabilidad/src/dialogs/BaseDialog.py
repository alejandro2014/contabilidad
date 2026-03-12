from PySide2.QtWidgets import QDialog

from src.config.ConfigLoader import ConfigLoader

from src.widgets.BaseWidget import BaseWidget

class BaseDialog(QDialog, BaseWidget):
    def __init__(self, parent, dialog_id):
        super(BaseDialog, self).__init__(parent)

        info_dialog = ConfigLoader().load_config_file(f'dialogs/{dialog_id}')

        self.setWindowTitle(info_dialog['title'])
        self.resize(info_dialog['width'], info_dialog['height'])

        self.setModal(True)
