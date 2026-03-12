#from src.services.ComboBoxService import ComboBoxService
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView

from src.config.ConfigLoader import ConfigLoader

class WidgetCreator:
    def __init__(self):
        #self.__combobox_service = ComboBoxService()
        pass

    def create_button(self, button_text, button_image, button_action):
        button = QPushButton(button_text)
        button.setIcon(QtGui.QIcon("src/config/images/" + button_image + ".png"))
        button.clicked.connect(button_action)

        return button

    def create_table(self, table_type, row_objects):
        table_info = ConfigLoader().load_table(table_type)
        titles=[ r['text'] for r in table_info ]
        fields=[ r['field'] for r in table_info ]

        table = QTableWidget()
        
        table.setColumnCount(len(titles))
        table.setHorizontalHeaderLabels(titles)
        table.setRowCount(len(row_objects))

        for i, row in enumerate(row_objects):
            for j in range(len(fields)):
                print(getattr(row, fields[j]))
                table.setItem(i, j, QTableWidgetItem(str(getattr(row, fields[j]))))

        table.resizeColumnsToContents()
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        return table

    def create_combobox(self, method_name):
        if self.__combobox_service is None:
            return None
        
        method_name = f'get_{method_name}s'
        values = getattr(self.__combobox_service, method_name)()
        combo = QComboBox()

        for value in values:
            combo.addItem(value)

        return combo
    
    def create_categories_combobox(self):
        return self.create_combobox('categorie')

