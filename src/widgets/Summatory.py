from PySide6 import QtCore
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

from src.widgets.charts.ChartPalette import ChartPalette

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
        self.update_expenses_sum_from_amounts([ ex.amount for ex in expenses ])

    def update_expenses_sum_from_amounts(self, amounts):
        # Expenses are stored as negative amounts, but the sum shows how much has been spent
        total_value = -sum([ float(amount) for amount in amounts ])

        # Adding 0.0 avoids showing "-0.0" when the amounts cancel out
        self.set_sum_value(round(total_value, 2) + 0.0)

    def update_expenses_sum_from_chart(self, amounts):
        total_value = sum([ float(amount) for amount in amounts ])

        self.set_sum_value(round(total_value, 2))

    def set_sum_value(self, value):
        self.lbl.setText(ChartPalette().format_amount(value))

    def set_records_no_value(self, value):
        self.lbl2.setText(str(value) + ' registros')

    def create_label(self, font_size):
        font = QFont('Monospace', font_size)

        label = QLabel()
        label.setFont(font)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        return label
