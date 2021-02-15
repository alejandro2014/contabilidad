from PySide2 import QtWidgets, QtGui
from PySide2.QtWidgets import QDialog, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit

from src.dialogs.InfoDialog import InfoDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.UseCasesService import UseCasesService


class LoadFileDialog(QDialog):
    def __init__(self, parent, listeners_pool):
        super(LoadFileDialog, self).__init__(parent)

        self.listeners_pool = listeners_pool

        widget_creator = WidgetCreator()

        self.use_cases_service = UseCasesService()

        self.setWindowTitle("Cargar fichero...")
        self.resize(400, 100)
        self.setModal(True)

        layout = QGridLayout()
        self.setLayout(layout)

        load_file_label = QLabel("Ruta del fichero:")
        self.load_file_textbox = QLineEdit()
        load_file_label.setBuddy(self.load_file_textbox)

        button_load = widget_creator.create_button("Cargar fichero", "upload", self.load_file)
        button_cancel = widget_creator.create_button("Cancelar", "cancel", self.reject)
        button_search = widget_creator.create_button("", "search", self.choose_file)

        button_box = QHBoxLayout()
        button_box.addWidget(button_load)
        button_box.addWidget(button_cancel)

        layout.addWidget(load_file_label, 0, 0)
        layout.addWidget(self.load_file_textbox, 0, 1)
        layout.addWidget(button_search, 0, 2)
        layout.addLayout(button_box, 1, 1)

        self.show()

    def choose_file(self):
        file_dialog = QFileDialog()
        file_name = file_dialog.getOpenFileName()

        self.load_file_textbox.insert(file_name[0])

    def load_file(self):
        file_name = self.load_file_textbox.text()
        values = self.use_cases_service.load_file(file_name)

        self.listeners_pool.send_event('pending-expenses-table', 'refresh_rows')

        message = "Registros cargados: " + str(values['inserted']) + "\nRegistros ignorados: " + str(values['ignored'])
        info_dialog = InfoDialog(self, title="Cargado fichero", message=message)

        #TODO Check whether file exists
        #TODO Check extension is correct

        self.load_file_textbox.clear()
