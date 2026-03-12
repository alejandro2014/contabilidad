from CsvReader import CsvReader
from ExpensesProcessor import ExpensesProcessor

from backup.contabilidad2.dao.files_dao import FilesDao

from services.ExpensesService import ExpensesService

class FilesService:
    def __init__(self):
        self.files_dao = FilesDao()

        self._csv_reader = CsvReader(self.get_line_transform())
        self._expenses_processor = ExpensesProcessor()

        self._expenses_service = ExpensesService()

    def load_file(self, file_path, classify):
        expenses, hash = self._csv_reader.read_file(file_path)

        if self.is_file_loaded(hash):
            print(f"Info: The file {file_path} is already loaded")
            return

        if classify:
            expenses = self._expenses_service.classify_expenses(expenses=expenses)

        self._expenses_service.load_expenses(expenses, hash)

        self.files_dao.add_file(hash, file_path)

    def delete_file(self, hash_file):
        is_file_loaded = self.files_dao.is_file_loaded(hash_file)

        if not is_file_loaded:
            print(f'Error: The file with hash {hash_file} does not exist')
            return

        self.files_dao.delete_file(hash_file)
        self._expenses_service.delete_expenses(hash_file)

    def is_file_loaded(self, hash):
        return self.files_dao.is_file_loaded(hash)

    def get_loaded_files(self):
        return self.files_dao.get_loaded_files()

    def get_line_transform(self):
        return lambda l: {
            'date': l[0],
            'category1_ing': l[1],
            'category2_ing': l[2],
            'concept': l[3],
            'amount': float(l[5].replace(',', ''))
        }
