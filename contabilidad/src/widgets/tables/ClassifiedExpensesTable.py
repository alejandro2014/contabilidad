import copy

from src.config.ConfigLoader import ConfigLoader

from src.services.ClassifiedExpensesService import ClassifiedExpensesService

from src.widgets.tables.BaseTable import BaseTable

from globals import widgets_pool as wpool

class ClassifiedExpensesTable(BaseTable):
    def __init__(self, table_type):
        self.table_name = 'classified-expenses-table'
        self.table_type = table_type

        info_file = f"classified-{table_type.replace('_', '-')}"
        self.table_info = ConfigLoader().load_table(info_file)

        self.expenses_service = ClassifiedExpensesService()
        self.expenses = []

        super(ClassifiedExpensesTable, self).__init__(self.table_name, self.table_info)

    def refresh(self, filter=None):
        self.expenses = getattr(self.expenses_service, f'get_{self.table_type}')(filter)
        expenses = copy.deepcopy(self.expenses)

        if self.table_type == 'expenses_raw':
            expenses = list(map(lambda ex: self.format_expense(ex), expenses))

        self.populate(expenses)
        wpool.execute('sum-text', 'update_expenses_sum_from_table', expenses)
        wpool.execute('sum-text', 'set_records_no_value', len(expenses))
