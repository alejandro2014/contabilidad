import json
import pandas as pd

from FileReader import FileReader
from src.services.PendingExpensesService import PendingExpensesService

from src.config.ConfigLoader import ConfigLoader

class UseCasesService:
    def __init__(self):
        self.expenses_service = PendingExpensesService()
        self.config_loader = ConfigLoader()

    def load_file(self, file_name):
        if file_name.endswith('.xls'):
            expenses = self.extract_expenses_from_xls(file_name)

        if file_name.endswith('.csv'):
            expenses = self.extract_expenses_from_csv(file_name)
        
        return self.insert_expense_lines(expenses)

    def insert_expense_lines(self, expense_lines, formatter=None):
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
    
    def extract_expenses_from_xls(self, xls_name):
        df = pd.read_excel(xls_name)

        rows_number = df.shape[0]

        df = df[4 : rows_number-1]
        df.columns = ['date', 'category', 'subcategory', 'concept', 'comment', 'value']
        df = df.drop(['comment'], axis=1)

        return [ {
            'date': str(r['date'].date()).replace('-', ''),
            'category': r['category'],
            'subcategory': r['subcategory'],
            'concept': r['concept'],
            'value': float(r['value'])
        } for _, r in df.iterrows() ]

    def extract_expenses_from_csv(self, csv_name):
        reader_info = ConfigLoader().load_config_file('csv/csv-loader')
        print(reader_info)
        file_reader = FileReader(reader_info)
        expense_lines = file_reader.read_file(csv_name)

        return self.insert_expense_lines(expense_lines, reader_info)
