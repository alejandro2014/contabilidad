from PySide2 import QtWidgets
from PySide2.QtWidgets import QDialog, QFileDialog, QGridLayout, QMessageBox

from src.dialogs.BaseDialog import BaseDialog

from src.services.UseCasesService import UseCasesService

from globals import widgets_pool as wpool

class LoadFileDialog(BaseDialog):
    def __init__(self, parent):
        self.id = 'load-file-dialog'

        super(LoadFileDialog, self).__init__(parent, self.id)

        self.use_cases_service = UseCasesService()

        self.load_file_label, self.load_file_textbox = self.create_line_edit("Ruta del fichero:")
        self.button_search = self.create_button("", "search", self.choose_file)
        self.button_box = self.create_button_box(self.id)

        self.create_layout()
        self.show()

    def create_layout(self):
        layout = QGridLayout()

        layout.addWidget(self.load_file_label, 0, 0)
        layout.addWidget(self.load_file_textbox, 0, 1)
        layout.addWidget(self.button_search, 0, 2)
        layout.addLayout(self.button_box, 1, 1)

        self.setLayout(layout)

    def choose_file(self):
        file_dialog = QFileDialog()
        file_name = file_dialog.getOpenFileName()

        self.load_file_textbox.insert(file_name[0])

    def load_file(self):
        file_name = self.load_file_textbox.text()

        if self.input_error(file_name):
            return

        values = self.use_cases_service.load_file(file_name)

        wpool.execute('pending-expenses-table', 'refresh')
        wpool.execute('menubar', 'refresh')
        wpool.execute('date-filter', 'update_top_dates')

        message = f"Registros cargados: {str(values['inserted'])}\nRegistros ignorados: {str(values['ignored'])}"
        QMessageBox.information(self, "Cargado fichero", message)

        self.load_file_textbox.clear()

    def input_error(self, file_name):
        if file_name == '':
            QMessageBox.warning(self, "No se ha seleccionado un fichero", "El nombre de fichero no puede estar vacío")
            return True

        if not file_name.endswith('.csv'):
            QMessageBox.warning(self, "Extensión incorrecta", 'La extensión del fichero ha de ser ".csv"')
            return True

        try:
            file = open(file_name, 'r')
        except IOError:
            QMessageBox.warning(self, "No se ha podido abrir el fichero", f"Ha habido un error abriendo el fichero:\n\n {file_name}\n\nCompruebe que el fichero existe.")
            return True

        file.close()

        return False
