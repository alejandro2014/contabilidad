from PySide2 import QtCore, QtGui
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

class Summatory(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(Summatory, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'sum-text', listeners_pool)

        self.lbl = self.create_label(22)
        self.lbl2 = self.create_label(12)

        layout = QVBoxLayout()
        self.setLayout(layout)

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.lbl)
        inner_layout.addWidget(self.lbl2)

        group_box = QGroupBox("Sumatorio")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.set_sum_value(0.0)
        self.set_records_no_value(0)

    def hide_records_no(self):
        self.lbl2.hide()

    def show_records_no(self):
        self.lbl2.show()

    def update_expenses_sum_from_table(self, expenses):
        values = list(map(lambda ex: ex['quantity'], expenses))

        sum = 0.0

        for value in values:
            sum += float(value)

        sum = round(sum, 2)

        self.set_sum_value(sum)

    def update_expenses_sum_from_chart(self, categories):
        sum = 0.0

        values = categories.values()

        for value in values:
            sum += float(value)

        sum = round(sum, 2)

        self.set_sum_value(sum)

    def set_sum_value(self, value):
        #TODO Set color depending on the value

        self.lbl.setText(str(value) + ' €')

    def set_records_no_value(self, value):
        self.lbl2.setText(str(value) + ' registros')

    def create_label(self, font_size):
        font = QFont('Monospace', font_size)

        label = QLabel()
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        return label
