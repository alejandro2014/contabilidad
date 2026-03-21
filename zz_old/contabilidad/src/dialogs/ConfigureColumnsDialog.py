from PySide2.QtCore import Qt
from PySide2.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout

from src.dialogs.BaseDialog import BaseDialog

from src.services.FileLoaderService import FileLoaderService

from src.widgets.ComboBox import ComboBox
from src.widgets.GroupBox import GroupBox
from src.widgets.LineEdit import LineEdit

class ConfigureColumnsDialog(BaseDialog):
    def __init__(self, parent):
        self.parent = parent
        self.id = 'configure-fields-dialog'

        super(ConfigureColumnsDialog, self).__init__(self.parent, self.id)

        self.file_loader_service = FileLoaderService()

        self.file_type = ComboBox('Tipo de fichero', 'get_file_types')

        self.has_header = QCheckBox('Tiene cabecera')
        self.prefix = LineEdit("Prefijo:")

        self.file_group_box = GroupBox("Campos del fichero", [ self.file_type, self.has_header, self.prefix ])

        self.date = LineEdit("Fecha:")
        self.concept = LineEdit("Concepto:")
        self.quantity = LineEdit("Cantidad:")
        self.fields_group_box = GroupBox("Números de posicion", [ self.date, self.concept, self.quantity ])

        button_box = self.create_button_box(self.id)

        self.create_layout()
        self.show()

        self.load_values()
        self.disableElements()

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.file_group_box)
        layout.addWidget(self.fields_group_box)
        # layout.addLayout(button_box)

        self.setLayout(layout)

    def load_values(self):
        reader_info = self.file_loader_service.get_file_loader_values()

        has_header = reader_info['hasHeader']
        prefix = reader_info['fieldNamePrefix']

        date_pos = str(reader_info['fields']['date'])
        concept_pos = str(reader_info['fields']['concept'])
        quantity_pos = str(reader_info['fields']['value'])

        self.has_header.setCheckState(Qt.Checked if has_header else Qt.UnChecked)

        self.prefix.setText(prefix)

        self.date.setText(date_pos)
        self.concept.setText(concept_pos)
        self.quantity.setText(quantity_pos)

    # TODO Make program able to modify elements
    def disableElements(self):
        self.file_type.setEnabled(False)
        self.has_header.setEnabled(False)
        self.prefix.setEnabled(False)

        self.date.setEnabled(False)
        self.concept.setEnabled(False)
        self.quantity.setEnabled(False)

    def save(self):
        pass

    def refresh(self):
        pass
