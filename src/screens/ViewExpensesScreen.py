from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QWidget

from src.dialogs.InfoDialog import InfoDialog

from src.events.ListenerNode import ListenerNode
from src.events.ListenersPool import ListenersPool

from src.services.ExportService import ExportService

from src.widgets.FilterWidget import FilterWidget

from src.widgets.tables.ClassifiedExpensesTable import ClassifiedExpensesTable

class ViewExpensesScreen(QWidget, ListenerNode):
    def __init__(self, listeners_pool, filter=None, *args, **kwargs):
        super(ViewExpensesScreen, self).__init__(*args, **kwargs)

        self.listeners_pool = listeners_pool
        ListenerNode.__init__(self, 'view-expenses-screen', self.listeners_pool)

        self.classified_expenses_table = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.filter_widget = FilterWidget('classified', listeners_pool)
        self.layout.addWidget(self.filter_widget)

        # Opened from a chart of the dashboard, with the movements behind it
        if filter is not None:
            self.filter_widget.set_filter(filter)

        self.add_table('expenses_raw')
        self.send_event('sum-text', 'show_records_no')

    def add_table(self, table_type):
        if self.classified_expenses_table != None:
            self.layout.removeWidget(self.classified_expenses_table)

        self.classified_expenses_table = ClassifiedExpensesTable(self.listeners_pool, table_type)
        self.classified_expenses_table.refresh_rows(self.filter_widget.filter)
        self.layout.addWidget(self.classified_expenses_table)

        # Grouped rows are not single expenses, so they can't be unclassified nor have notes
        self.filter_widget.unclassify_button.setEnabled(table_type == 'expenses_raw')
        self.filter_widget.notes_button.setEnabled(table_type == 'expenses_raw')

    def export_table(self):
        file_name, selected_filter = QFileDialog.getSaveFileName(self, 'Exportar movimientos', 'movimientos.xlsx', 'Excel (*.xlsx);;CSV (*.csv)')

        if file_name == '':
            return

        # The format is the one of the extension, or of the type chosen when it is typed without it
        if not file_name.lower().endswith(('.xlsx', '.csv')):
            file_name += '.csv' if 'csv' in selected_filter.lower() else '.xlsx'

        header, rows = self.classified_expenses_table.export_rows()
        ExportService().export_table(file_name, header, rows)

        InfoDialog(self, title = 'Movimientos exportados', message = f'Se ha guardado en {file_name}')
