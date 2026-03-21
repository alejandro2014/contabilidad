import copy

from src.config.ConfigLoader import ConfigLoader

from src.services.PendingExpensesService import PendingExpensesService

from src.widgets.tables.BaseTable import BaseTable

from globals import widgets_pool as wpool

class PendingExpensesTable(BaseTable):
    def __init__(self):
        self.table_name = 'pending-expenses-table'
        self.table_info = ConfigLoader().load_table('pending-expenses')

        self.expenses_service = PendingExpensesService()
        self.expenses = []

        super(PendingExpensesTable, self).__init__(self.table_name, self.table_info)

    def get_widgets_from_pool(self):
        pass

    def create_layout(self):
        pass

    def init_widgets(self):
        pass

    def refresh(self, filter = None):
        self.expenses = self.expenses_service.get_expenses(filter)

        expenses = copy.deepcopy(self.expenses)
        expenses = list(map(lambda ex: self.format_expense(ex), expenses))

        self.populate(expenses)

        wpool.execute('sum-text', 'update_expenses_sum_from_table', expenses)
        wpool.execute('sum-text', 'set_records_no_value', len(expenses))
