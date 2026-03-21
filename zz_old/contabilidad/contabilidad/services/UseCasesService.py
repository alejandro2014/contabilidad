from FileReader import FileReader
from services.ExpensesService import ExpensesService

class UseCasesService:
    def __init__(self):
        self.expenses_service = ExpensesService()

    def load_file(self, file_name):
        reader_info = {
            'readerType': 'csv',
            'hasHeader': 'false',
            'fieldNamePrefix': 'field_',
            'separator': '\t'
        }

        file_reader = FileReader(reader_info)
        expense_lines = file_reader.read_file(file_name)
        self.insert_expense_lines(expense_lines)

    def insert_expense_lines(self, expense_lines):
        inserted = 0
        ignored = 0

        for expense_line in expense_lines:
            if self.expenses_service.add_expense(expense_line):
                inserted += 1
            else:
                ignored += 1

        print("Inserted: " + str(inserted) + ", Ignored: " + str(ignored))
