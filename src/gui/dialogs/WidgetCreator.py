from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView

from src.config.ConfigLoader import ConfigLoader

class WidgetCreator:
    def create_table(self, table_type, row_objects):
        table_info = ConfigLoader().load_table(table_type)
        titles=[ r['text'] for r in table_info ]
        fields=[ r['field'] for r in table_info ]

        table = QTableWidget()
        
        table.setColumnCount(len(titles))
        table.setHorizontalHeaderLabels(titles)
        table.setRowCount(len(row_objects))

        for i, row in enumerate(row_objects):
            for j in range(len(fields)):
                print(getattr(row, fields[j]))
                table.setItem(i, j, QTableWidgetItem(str(getattr(row, fields[j]))))

        table.resizeColumnsToContents()
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        return table