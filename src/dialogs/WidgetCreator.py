from src.services.ComboBoxService import ComboBoxService
from PySide2 import QtWidgets, QtGui
from PySide2.QtWidgets import QComboBox, QPushButton, QTableWidget, QTableWidgetItem

class WidgetCreator:
    def __init__(self):
        self.__combobox_service = ComboBoxService()

    def create_button(self, button_text, button_image, button_action):
        button = QPushButton(button_text)
        button.setIcon(QtGui.QIcon("src/config/images/" + button_image + ".png"))
        button.clicked.connect(button_action)

        return button

    def create_table(self, table_info, table_rows):
        table = QTableWidget(1, len(table_info))
        column_labels = map(lambda x: x['field_text'], table_info)
        table.setHorizontalHeaderLabels(column_labels)

        categories = list(map(lambda x: x['field'], table_info))

        for index_row, table_row in enumerate(table_rows):
            table.insertRow(index_row)

            for index_category, category in enumerate(categories):
                table.setItem(index_row, index_category, QTableWidgetItem(table_row[category]))

        table.resizeColumnsToContents()

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

