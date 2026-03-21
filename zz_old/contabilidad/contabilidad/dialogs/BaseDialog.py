from PySide6 import QtWidgets, QtGui

class BaseDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(BaseDialog, self).__init__(parent)

    def create_button(self, button_text, button_image, button_action):
        button = QtWidgets.QPushButton(button_text, self)
        button.setIcon(QtGui.QIcon("images/" + button_image + ".png"))
        button.clicked.connect(button_action)

        return button
