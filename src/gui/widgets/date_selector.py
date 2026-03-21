from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from src.gui.widgets.combobox import ComboBox

from src.services.combobox_services.days_service import DaysService
from src.services.combobox_services.months_service import MonthsService
from src.services.combobox_services.years_service import YearsService


class DateSelector(QWidget):
    def __init__(self, title):
        super().__init__()

        layout = QHBoxLayout(self)

        layout.addWidget(QLabel(title + ':'))
        layout.addWidget(ComboBox(combobox_service=DaysService()))
        layout.addWidget(ComboBox(combobox_service=MonthsService()))
        layout.addWidget(ComboBox(combobox_service=YearsService()))