from src.dao.FileLoaderSqlGenerator import FileLoaderSqlGenerator

from src.services.BaseService import BaseService
from src.services.formatters.FileLoaderFormatter import FileLoaderFormatter

class FileLoaderService(BaseService):
    def __init__(self):
        super().__init__()

        self.sql_generator = FileLoaderSqlGenerator()
        self.formatter = FileLoaderFormatter()

    def get_file_loader_values(self):
        sql = self.sql_generator.select_file_loader_values()
        file_loader_values_raw = self.db.select(sql)
        file_loader_values = self.formatter.format_file_loader_values(file_loader_values_raw)

        return file_loader_values
