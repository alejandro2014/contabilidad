from PySide2 import QtWidgets, QtGui
from PySide2.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

from src.config.ConfigLoader import ConfigLoader

from src.services.ComboBoxService import ComboBoxService

from globals import widgets_pool as wpool

class BaseWidget:
    def create_button(self, button_text, button_image, button_action):
        button = QPushButton(button_text)
        button.setIcon(QtGui.QIcon(f"src/config/images/{button_image}.png"))
        button.clicked.connect(button_action)

        return button

    def create_button_box(self, config_file_name):
        buttons_info = ConfigLoader().load_config_file(f'button-boxes/{config_file_name}')
        button_box = QHBoxLayout()

        for button_info in buttons_info:
            method = getattr(self, button_info['action'])
            button = self.create_button(button_info['text'], button_info['image'], method)
            button_box.addWidget(button)

        return button_box

    def create_combobox(self, method_name, service=None):
        if not service:
            service = ComboBoxService()

        combo = QComboBox()
        values = getattr(service, method_name)()

        for value in values:
            combo.addItem(value)

        return combo

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

    def add_rows(self):
        pass

    def create_line_edit(self, text):
        label = QLabel(text)
        line_edit = QLineEdit()
        label.setBuddy(line_edit)

        return label, line_edit

    def create_group_box(self, title, fields):
        layout = QVBoxLayout()

        for field in fields:
            self.add_text_field_layout(layout, field)

        group_box = QGroupBox(title)
        group_box.setLayout(layout)

        return group_box

    def add_text_field_layout(self, layout, field):
        field_layout = self.create_text_field_layout(field)
        layout.addLayout(field_layout)

    def create_text_field_layout(self, field):
        layout = QHBoxLayout()
        layout.addWidget(field[0])
        layout.addWidget(field[1])

        return layout
