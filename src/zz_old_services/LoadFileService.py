import numpy as np
import pandas as pd
import uuid

from FileReader import FileReader
from src.services.expenses_service import ExpensesService

from src.config.ConfigLoader import ConfigLoader

from src.model.expense import Expense

class LoadFileService:
    def __init__(self):
        self.expenses_service = ExpensesService()
        self.config_loader = ConfigLoader()

    def load_file(self, file_name):
        if file_name.endswith('.xls'):
            expenses = self.extract_expenses_from_xls(file_name)

        if file_name.endswith('.csv'):
            expenses = self.extract_expenses_from_csv(file_name)
        
        return self.insert_expense_lines(expenses)

    def insert_expense_lines(self, expenses):
        successes, errors = self.expenses_service.load_expenses(expenses)

        return {
            'inserted': successes,
            'ignored': errors
        }
    
    def extract_expenses_from_xls(self, xls_name):
        df = pd.read_excel(xls_name)

        rows_number = df.shape[0]

        df = df[4 : rows_number-1]
        df.columns = ['date', 'category', 'subcategory', 'concept', 'comment', 'value']
        df = df.drop(['comment'], axis=1)

        return [
            self.debug_expense(r)
             for _, r in df.iterrows()
        ]
    
    def debug_expense(self, r):
        expense = Expense(
            id = str(uuid.uuid4()),
            date = str(r['date'].date()).replace('-', ''),
            category_src = self.format_nan(r['category']),
            subcategory_src = self.format_nan(r['subcategory']),
            title = r['concept'],
            amount = float(r['value'])
        )

        print(expense)

        return expense

    def extract_expenses_from_csv(self, csv_name):
        reader_info = ConfigLoader().load_config_file('csv/csv-loader')
        file_reader = FileReader(reader_info)
        expense_lines = file_reader.read_file(csv_name)

        return self.insert_expense_lines(expense_lines, reader_info)
    
    def format_nan(self, value):
        return None if value == np.nan else value
