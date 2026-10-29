from PySide6 import QtCore
from PySide6.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

from src.events.ListenerNode import ListenerNode

class SecondaryFilters(QWidget, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(SecondaryFilters, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'secondary-filters', listeners_pool)

        self.group_by_month = QCheckBox('Por mes')
        self.group_by_type = QCheckBox('Por tipo de gasto')
        # The totals of each tag of the range, alone: a movement can have several tags
        self.group_by_tag = QCheckBox('Por etiqueta')

        layout = QVBoxLayout()
        self.setLayout(layout)

        inner_layout = QHBoxLayout()
        inner_layout.addWidget(self.group_by_month)
        inner_layout.addWidget(self.group_by_type)
        inner_layout.addWidget(self.group_by_tag)

        group_box = QGroupBox('Agrupaciones')
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.group_by_month.stateChanged.connect(self.grouping_changed)
        self.group_by_type.stateChanged.connect(self.grouping_changed)
        self.group_by_tag.stateChanged.connect(self.grouping_changed)

    def grouping_changed(self):
        month_status = self.group_by_month.checkState()
        type_status = self.group_by_type.checkState()
        by_tag = self.group_by_tag.isChecked()

        self.group_by_month.setEnabled(not by_tag)
        self.group_by_type.setEnabled(not by_tag)

        if by_tag:
            criteria = 'expenses_by_tag'
        elif month_status == QtCore.Qt.CheckState.Unchecked and type_status == QtCore.Qt.CheckState.Unchecked:
            criteria = 'expenses_raw'
        elif month_status == QtCore.Qt.CheckState.Unchecked and type_status == QtCore.Qt.CheckState.Checked:
            criteria = 'expenses_by_type'
        elif month_status == QtCore.Qt.CheckState.Checked and type_status == QtCore.Qt.CheckState.Unchecked:
            criteria = 'expenses_by_month'
        elif month_status == QtCore.Qt.CheckState.Checked and type_status == QtCore.Qt.CheckState.Checked:
            criteria = 'expenses_by_type_and_month'

        self.send_event('view-expenses-screen', 'add_table', criteria)
