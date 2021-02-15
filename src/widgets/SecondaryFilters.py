from PySide2 import QtCore
from PySide2.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

class SecondaryFilters(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(SecondaryFilters, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'secondary-filters', listeners_pool)

        self.group_by_month = QCheckBox('Por mes')
        self.group_by_type = QCheckBox('Por tipo de gasto')

        layout = QVBoxLayout()
        self.setLayout(layout)

        inner_layout = QHBoxLayout()
        inner_layout.addWidget(self.group_by_month)
        inner_layout.addWidget(self.group_by_type)

        group_box = QGroupBox('Agrupaciones')
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.group_by_month.stateChanged.connect(self.grouping_changed)
        self.group_by_type.stateChanged.connect(self.grouping_changed)

    def grouping_changed(self):
        month_status = self.group_by_month.checkState()
        type_status = self.group_by_type.checkState()

        if month_status == QtCore.Qt.CheckState.Unchecked and type_status == QtCore.Qt.CheckState.Unchecked:
            criteria = 'expenses_raw'
        elif month_status == QtCore.Qt.CheckState.Unchecked and type_status == QtCore.Qt.CheckState.Checked:
            criteria = 'expenses_by_type'
        elif month_status == QtCore.Qt.CheckState.Checked and type_status == QtCore.Qt.CheckState.Unchecked:
            criteria = 'expenses_by_month'
        elif month_status == QtCore.Qt.CheckState.Checked and type_status == QtCore.Qt.CheckState.Checked:
            criteria = 'expenses_by_type_and_month'

        self.send_event('view-expenses-screen', 'add_table', criteria)
