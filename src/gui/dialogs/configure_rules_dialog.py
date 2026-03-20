from PySide6 import QtWidgets
from PySide6.QtWidgets import QAbstractItemView, QDialog, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QTimer

from src.config.ConfigLoader import ConfigLoader

from src.gui.dialogs.add_category_dialog import AddCategoryDialog
from src.gui.dialogs.WidgetCreator import WidgetCreator

from src.services.rules_service import RulesService


class ConfigureRulesDialog(QDialog):
    def __init__(self, parent):
        super(ConfigureRulesDialog, self).__init__(parent)

        self.titles, self.fields = self.get_table_info('rules')

        self.table = QTableWidget()
        self.table.setHorizontalHeaderLabels(self.titles)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table.setSortingEnabled(True)
        QTimer.singleShot(0, lambda: self.table.sortItems(0))

        self.widget_creator = WidgetCreator()
        self.service = RulesService()

        self.setWindowTitle("Configuración de reglas")
        self.resize(600, 400)
        self.setModal(True)

        self.refresh()

        button_add = self.widget_creator.create_button("Añadir regla", "upload", self.add_rule)
        button_remove = self.widget_creator.create_button("Eliminar seleccionadas", "bin", self.remove_selected_rows)
        button_ok = self.widget_creator.create_button("Aceptar", "ok", self.accept)

        button_box = QtWidgets.QHBoxLayout()
        button_box.addWidget(button_add)
        button_box.addWidget(button_remove)
        button_box.addWidget(button_ok)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_box)

        self.setLayout(self.layout)
        self.show()
    
    def refresh(self):
        row_objects = self.service.get_rules()
        self.refresh_table(self.table, titles=self.titles, fields=self.fields, row_objects=row_objects)

    def refresh_table(self, table, titles, fields, row_objects):
        table.setSortingEnabled(False)
        table.clearContents()
        table.setColumnCount(len(titles))
        table.setRowCount(len(row_objects))

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
            self.categories_service.add_category(name, description)
            self.refresh()

    def remove_selected_rows(self):
        selected_rows = self.table.selectionModel().selectedRows()

        categories = [ self.table.model().index(r.row(), 0).data() for r in selected_rows ]

        self.categories_service.delete_categories(categories)
        self.refresh()

    def get_table_info(self, table_id):
        table_info = ConfigLoader().load_table(table_id)

        titles = [ r['text'] for r in table_info ]
        fields = [ r['field'] for r in table_info ]

        return titles, fields
