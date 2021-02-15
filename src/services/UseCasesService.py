import json

from FileReader import FileReader
from src.services.PendingExpensesService import PendingExpensesService

from src.config.ConfigLoader import ConfigLoader

class UseCasesService:
    def __init__(self):
        self.expenses_service = PendingExpensesService()
        self.config_loader = ConfigLoader()

    def load_file(self, file_name):
        reader_info = ConfigLoader().load_config_file('csv/csv-loader')
        print(reader_info)
        file_reader = FileReader(reader_info)
        expense_lines = file_reader.read_file(file_name)

        return self.insert_expense_lines(expense_lines, reader_info)

    def insert_expense_lines(self, expense_lines, formatter):
        inserted = 0
        ignored = 0

        for expense_line in expense_lines:
            if self.expenses_service.add_expense(expense_line, formatter):
                inserted += 1
            else:
                ignored += 1

        return {
            'inserted': inserted,
            'ignored': ignored
        }
