import os

from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QDialog, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit

from src.dialogs.ErrorDialog import ErrorDialog
from src.dialogs.InfoDialog import InfoDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.LoadFileService import LoadFileService
from src.logger import get_logger

logger = get_logger(__name__)

class LoadFileDialog(QDialog):
    def __init__(self, parent, listeners_pool):
        super(LoadFileDialog, self).__init__(parent)

        self.listeners_pool = listeners_pool

        widget_creator = WidgetCreator()

        self.expenses_service = LoadFileService()

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
        # Only the xls bank statements can be loaded
        file_name = file_dialog.getOpenFileName(self, 'Cargar fichero', '', 'Extracto bancario (*.xls)')

        # Empty when the dialog is cancelled
        if file_name[0] != '':
            self.load_file_textbox.setText(file_name[0])

    def load_file(self):
        file_name = self.load_file_textbox.text().strip()

        error = self.check_file(file_name)

        if error is not None:
            ErrorDialog(self, title="Error al cargar el fichero", message=error)
            return

        try:
            values = self.expenses_service.load_file(file_name)
        except ValueError as e:
            # The file has no F. VALOR header: it is not a bank statement
            logger.error(f'{file_name} can not be loaded: {e}')
            ErrorDialog(self, title="Error al cargar el fichero", message="El fichero no es un extracto bancario: no tiene la cabecera \"F. VALOR\".\nNo se ha cargado ningún registro.")
            return
        except Exception as e:
            logger.exception(f'{file_name} can not be loaded')
            ErrorDialog(self, title="Error al cargar el fichero", message=f"No se ha podido cargar el fichero: {e}\nNo se ha cargado ningún registro.")
            return

        self.listeners_pool.send_event('pending-expenses-table', 'refresh_rows')
        self.listeners_pool.send_event('status-bar', 'refresh')

        message = f"Registros cargados: {str(values['inserted'])}\nRegistros ignorados: {str(values['ignored'])}"
        info_dialog = InfoDialog(self, title="Cargado fichero", message=message)

        self.load_file_textbox.clear()

    def check_file(self, file_name):
        # The error to show, or None when the file can be loaded
        if file_name == '':
            return "Elige el fichero que quieres cargar"

        if not os.path.isfile(file_name):
            return f'El fichero "{file_name}" no existe'

        if os.path.splitext(file_name)[1].lower() != '.xls':
            return "Solo se pueden cargar extractos bancarios en formato .xls"

        return None
