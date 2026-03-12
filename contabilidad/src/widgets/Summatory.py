from PySide2 import QtCore, QtGui
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from globals import widgets_pool as wpool

from src.widgets.RootWidget import RootWidget

class Summatory(RootWidget):
    def __init__(self):
        super().__init__()

        self.amount_label = self.create_label(font_size=22)
        self.records_label = self.create_label(font_size=12)

    def init_widgets(self):
        self.set_sum_value(0.0)
        self.set_records_no_value(0)

    def create_layout(self):
        layout = QVBoxLayout()

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.amount_label)
        inner_layout.addWidget(self.records_label)

        group_box = QGroupBox("Sumatorio")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.setLayout(layout)

    def hide_records_no(self):
        self.records_label.hide()

    def show_records_no(self):
        self.records_label.show()

    def update_expenses_sum_from_table(self, expenses):
        if len(expenses) == 0:
            self.set_sum_value(0.0)
            return

        values = list(map(lambda ex: ex['quantity'], expenses))
        self.update_expenses_sum(values)

    def update_expenses_sum_from_chart(self, categories):
        values = categories.values()
        self.update_expenses_sum(values)

    def update_expenses_sum(self, values):
        sum = 0.0

        for value in values:
            sum += float(value)

        sum = round(sum, 2)

        self.set_sum_value(sum)

    def set_sum_value(self, value):
        self.amount_label.setText(str(value) + ' €')

    def set_records_no_value(self, value):
        self.records_label.setText(str(value) + ' registros')

    def create_label(self, font_size):
        font = QFont('Monospace', font_size)

        label = QLabel()
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        return label
