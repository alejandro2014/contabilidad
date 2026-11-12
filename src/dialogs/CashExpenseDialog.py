import sqlite3

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QDateEdit, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLineEdit, QVBoxLayout

from src.dialogs.ErrorDialog import ErrorDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.ComboBoxService import ComboBoxService
from src.services.expenses_service import ExpensesService

class CashExpenseDialog(QDialog):
    # An expense paid with the cash taken from an ATM (see ExpensesService.add_cash_expense)
    def __init__(self, parent):
        super(CashExpenseDialog, self).__init__(parent)

        self.setWindowTitle('Gasto en efectivo')
        self.resize(400, 150)
        self.setModal(True)

        widget_creator = WidgetCreator()

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('dd/MM/yyyy')

        self.title_textbox = QLineEdit()
        self.title_textbox.setPlaceholderText('P. ej.: Mercado')

        self.amount_spinbox = QDoubleSpinBox()
        self.amount_spinbox.setRange(0, 1000000)
        self.amount_spinbox.setDecimals(2)
        self.amount_spinbox.setSuffix(' €')

        self.category_combobox = QComboBox()
        self.category_combobox.addItems([ c for c in ComboBoxService().get_categories() if c != ExpensesService.CASH_CATEGORY ])

        form = QFormLayout()
        form.addRow('Fecha:', self.date_edit)
        form.addRow('Concepto:', self.title_textbox)
        form.addRow('Importe:', self.amount_spinbox)
        form.addRow('Tipo de gasto:', self.category_combobox)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(widget_creator.create_button('Aceptar', 'ok', self.save))
        buttons_layout.addWidget(widget_creator.create_button('Cancelar', 'cancel', self.reject))

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def save(self):
        title = self.title_textbox.text().strip()
        amount = self.amount_spinbox.value()
        category = self.category_combobox.currentText()

        if title == '' or amount == 0 or category == '':
            ErrorDialog(self, title='Gasto en efectivo', message='Escribe el concepto, el importe y el tipo de gasto')
            return

        try:
            ExpensesService().add_cash_expense(self.date_edit.date().toString('yyyyMMdd'), title, amount, category)
        except sqlite3.IntegrityError:
            ErrorDialog(self, title='Gasto en efectivo', message='Ya hay un gasto con la misma fecha, concepto e importe')
            return

        self.accept()
