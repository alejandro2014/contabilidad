from PySide6.QtWidgets import QDialog, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit

from src.gui.dialogs.info_dialog import InfoDialog

from src.services.load_file_service import LoadFileService

from src.gui.widgets.pictured_button import PicturedButton


class LoadFileDialog(QDialog):
    def __init__(self, parent, listeners_pool):
        #self.parent = parent
        #super().__init__(self.parent)

        super(LoadFileDialog, self).__init__(parent)

        self.listeners_pool = listeners_pool

        self.expenses_service = LoadFileService()

        self.setWindowTitle("Cargar fichero...")
        self.resize(400, 100)
        self.setModal(True)

        layout = QGridLayout()
        self.setLayout(layout)

        load_file_label = QLabel("Ruta del fichero:")
        self.load_file_textbox = QLineEdit()
        load_file_label.setBuddy(self.load_file_textbox)

        
        button_load = PicturedButton("Cargar fichero", "upload", self.load_file)
        button_cancel = PicturedButton("Cancelar", "cancel", self.reject)
        button_search = PicturedButton("", "search", self.choose_file)

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
        values = self.expenses_service.load_file(file_name)

        self.listeners_pool.send_event('pending-expenses-table', 'refresh_rows')

        message = f"Registros cargados: {str(values['inserted'])}\nRegistros ignorados: {str(values['ignored'])}"
        info_dialog = InfoDialog(self, message=message)

        #TODO Check whether file exists
        #TODO Check extension is correct

        self.load_file_textbox.clear()