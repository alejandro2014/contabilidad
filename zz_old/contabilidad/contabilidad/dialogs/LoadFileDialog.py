from dialogs.BaseDialog import BaseDialog
from PySide6 import QtWidgets, QtGui

class LoadFileDialog(BaseDialog):
    def __init__(self, parent):
        super(LoadFileDialog, self).__init__(parent)

        self.parent = parent
        self.usecases_service = parent.get_use_cases_service()

        self.setWindowTitle("Cargar fichero...")

        self.resize(400, 100)
        self.setModal(True)

        load_file_label = QtWidgets.QLabel("Ruta del fichero:")
        self.load_file_textbox = QtWidgets.QLineEdit()
        load_file_label.setBuddy(self.load_file_textbox)

        button_load = self.create_button("Cargar fichero", "upload", self.load_file)
        button_cancel = self.create_button("Cancelar", "cancel", self.reject)
        button_search = self.create_button("", "search", self.choose_file)

        button_box = QtWidgets.QHBoxLayout()
        button_box.addWidget(button_load)
        button_box.addWidget(button_cancel)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(load_file_label, 0, 0)
        self.layout.addWidget(self.load_file_textbox, 0, 1)
        self.layout.addWidget(button_search, 0, 2)
        self.layout.addLayout(button_box, 1, 1)

        self.setLayout(self.layout)
        self.show()

    def choose_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_name = file_dialog.getOpenFileName()

        self.load_file_textbox.insert(file_name[0])

    def load_file(self):
        file_name = self.load_file_textbox.text()
        self.usecases_service.load_file(file_name)
        self.accept()
