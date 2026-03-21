from dialogs.BaseDialog import BaseDialog
from PySide6 import QtWidgets, QtGui

class ConfigureExpensesDialog(BaseDialog):
    def __init__(self, parent):
        super(ConfigureExpensesDialog, self).__init__(parent)

        self.parent = parent
        self.usecases_service = parent.get_use_cases_service()
        self.expense_types_service = parent.get_expense_types_service()

        self.setWindowTitle("Configuración de categorías")

        self.resize(600, 400)
        self.setModal(True)

        self.table_info = [
            {
                'field': 'category',
                'field_text': 'Tipo de gasto'
            },
            {
                'field': 'comment',
                'field_text': 'Comentarios'
            }
        ]

        self.table = QtWidgets.QTableWidget(1, len(self.table_info))
        self.columnLabels = map(lambda x: x['field_text'], self.table_info)
        self.table.setHorizontalHeaderLabels(self.columnLabels)

        expense_types = self.expense_types_service.get_expense_types_full()

        #categories = [ 'category', 'comment' ]
        categories = map(lambda x: x['field'], self.table_info)

        for index_row, expense_type in enumerate(expense_types):
            self.table.insertRow(index_row)

            for index_category, category in enumerate(categories):
                #print(expense_type[category])
                self.table.setItem(index_row, index_category, QtWidgets.QTableWidgetItem(expense_type[category]))

        self.table.resizeColumnsToContents()

        button_ok = self.create_button("Aceptar", "ok", self.accept)

        button_box = QtWidgets.QHBoxLayout()
        button_box.addWidget(button_ok)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_box)

        self.setLayout(self.layout)
        self.show()

    def remove_row(self):
        button = QtWidgets.QApplication.focusWidget()
        index = self.table.indexAt(button.pos())
        self.table.removeRow(index.row())
