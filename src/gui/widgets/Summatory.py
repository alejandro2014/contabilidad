from PySide6 import QtCore
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

class Summatory(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(Summatory, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'sum-text', listeners_pool)

        self.label_amount = self.create_label(font_size=22)
        self.label_records = self.create_label(font_size=12)

        layout = QVBoxLayout()
        self.setLayout(layout)

        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.label_amount)
        inner_layout.addWidget(self.label_records)

        group_box = QGroupBox("Sumatorio")
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.set_sum_value(0.0)
        self.set_records_no_value(0)

    def hide_records_no(self):
        self.label_records.hide()

    def show_records_no(self):
        self.label_records.show()

    def update_expenses_sum_from_table(self, expenses):
        total_value = sum([ float(ex.amount) for ex in expenses ])

        self.set_sum_value(round(total_value, 2))

    def update_expenses_sum_from_chart(self, categories):
        sum = 0.0

        values = categories.values()

        for value in values:
            sum += float(value)

        sum = round(sum, 2)

        self.set_sum_value(sum)

    def set_sum_value(self, value):
        #TODO Set color depending on the value
        currency = '€'
        self.label_amount.setText(f'{value} {currency}')

    def set_records_no_value(self, value):
        self.label_records.setText(f'{value} registros')

    def create_label(self, font_size=10):
        font = QFont('Monospace', font_size)

        label = QLabel()
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        return label
