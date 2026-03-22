from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from src.config.ConfigLoader import ConfigLoader


class Table(QTableWidget):
    def __init__(self, table_id=None, service=None, getter_name=None):
        super().__init__()

        self.table_id = table_id
        self.service = service
        self.getter_name = getter_name

        self.titles, self.fields = self._get_table_info(self.table_id)

    def refresh(self):
        row_objects = getattr(self.service, self.getter_name)()
    
        self.setSortingEnabled(False)
        self.clearContents()
        self.setColumnCount(len(self.titles))
        self.setRowCount(len(row_objects))
        self.setHorizontalHeaderLabels(self.titles)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        for i, row in enumerate(row_objects):
            for j in range(len(self.fields)):
                self.setItem(i, j, QTableWidgetItem(getattr(row, self.fields[j])))

        self.resizeColumnsToContents()

        self.setSortingEnabled(True)

    def remove_selected_rows(self):
        selected_rows = self.selectionModel().selectedRows()

        categories = [ self.model().index(r.row(), 0).data() for r in selected_rows ]

        self.service.delete_categories(categories)
        self.refresh()

    def _get_table_info(self, table_id):
        table_info = ConfigLoader().load_table(table_id)

        titles = [ r['text'] for r in table_info ]
        fields = [ r['field'] for r in table_info ]

        return titles, fields

