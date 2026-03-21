from PySide6 import QtWidgets
from PySide6.QtWidgets import QAbstractItemView, QDialog, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QTimer

from src.config.ConfigLoader import ConfigLoader

from src.gui.dialogs.add_category_dialog import AddCategoryDialog

from src.services.categories_service import CategoriesService

from src.gui.widgets.pictured_button import PicturedButton


class ConfigureExpensesDialog(QDialog):
    def __init__(self, parent):
        super(ConfigureExpensesDialog, self).__init__(parent)

        self.service = CategoriesService()
        self.table_id = 'expense-types'

        self.titles, self.fields = self.get_table_info(self.table_id)

        self.table = QTableWidget()
        self.table.setHorizontalHeaderLabels(self.titles)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setSortingEnabled(True)
        QTimer.singleShot(0, lambda: self.table.sortItems(0))

        self.setWindowTitle("Configuración de categorías")
        self.resize(600, 400)
        self.setModal(True)

        button_box = QtWidgets.QHBoxLayout()
        button_box.addWidget(PicturedButton("Añadir categoría", "upload", self.add_category))
        button_box.addWidget(PicturedButton("Eliminar seleccionadas", "bin", self.remove_selected_rows))
        button_box.addWidget(PicturedButton("Aceptar", "ok", self.accept))

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_box)

        self.setLayout(self.layout)
        self.show()

        self.refresh()
    
    def refresh(self):
        categories = self.service.get_categories()
        self.refresh_table(self.table, titles=self.titles, fields=self.fields, row_objects=categories)

    def refresh_table(self, table, titles, fields, row_objects):
        table.setSortingEnabled(False)
        table.clearContents()
        table.setColumnCount(len(titles))
        table.setRowCount(len(row_objects))
        table.setHorizontalHeaderLabels(titles)

        for i, row in enumerate(row_objects):
            for j in range(len(fields)):
                table.setItem(i, j, QTableWidgetItem(getattr(row, fields[j])))

        table.resizeColumnsToContents()

        table.setSortingEnabled(True)

        return table
    
    def add_category(self):
        dialog = AddCategoryDialog(self)

        if dialog.exec() == QDialog.Accepted:
            name, description = dialog.get_data()
            self.service.add_category(name, description)
            self.refresh()

    def remove_selected_rows(self):
        selected_rows = self.table.selectionModel().selectedRows()

        categories = [ self.table.model().index(r.row(), 0).data() for r in selected_rows ]

        self.service.delete_categories(categories)
        self.refresh()

    def get_table_info(self, table_id):
        table_info = ConfigLoader().load_table(table_id)

        titles = [ r['text'] for r in table_info ]
        fields = [ r['field'] for r in table_info ]

        return titles, fields
