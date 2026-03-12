from PySide2 import QtCore
from PySide2.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

from globals import widgets_pool as wpool

from src.widgets.RootWidget import RootWidget

class SecondaryFilters(RootWidget):
    def __init__(self):
        super().__init__()

        self.group_by_month = QCheckBox('Por mes')
        self.group_by_type = QCheckBox('Por tipo de gasto')

        self.group_by_month.stateChanged.connect(self.grouping_changed)
        self.group_by_type.stateChanged.connect(self.grouping_changed)

    def init_widgets(self):
        pass

    def create_layout(self):
        layout = QVBoxLayout()

        inner_layout = QHBoxLayout()
        inner_layout.addWidget(self.group_by_month)
        inner_layout.addWidget(self.group_by_type)

        group_box = QGroupBox('Agrupaciones')
        group_box.setLayout(inner_layout)

        layout.addWidget(group_box)

        self.setLayout(layout)

    def set_visibility_group_by_type(self, visibility):
        self.group_by_type.setVisible(visibility)

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

        wpool.execute('view-expenses-screen', 'add_table', criteria)
