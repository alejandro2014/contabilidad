import pandas as pd
import uuid

from src.services.expenses_service import ExpensesService
from src.services.RulesService import RulesService

from src.model.expense import Expense

class LoadFileService:
    def __init__(self):
        self.expenses_service = ExpensesService()
        self.rules_service = RulesService()

    def load_file(self, file_name):
        expenses = self.extract_expenses_from_xls(file_name)

        return self.insert_expense_lines(expenses)

    def insert_expense_lines(self, expenses):
        self.rules_service.classify_expenses(expenses)

        successes, errors = self.expenses_service.load_expenses(expenses)

        return {
            'inserted': successes,
            'ignored': errors
        }
    
    def extract_expenses_from_xls(self, xls_name):
        # Columns: F. VALOR, CATEGORÍA, SUBCATEGORÍA, DESCRIPCIÓN, COMENTARIO, IMPORTE (€), SALDO (€)
        columns = ['date', 'category', 'subcategory', 'concept', 'comment', 'value', 'balance']

        df = pd.read_excel(xls_name, header=None)

        header_row = self.find_xls_header_row(df)

        df = df.iloc[header_row + 1:, :len(columns)]
        df.columns = columns
        df = df.drop(['comment', 'balance'], axis=1)

        df['date'] = df['date'].map(lambda d: pd.to_datetime(d, dayfirst=True, errors='coerce'))
        df['value'] = df['value'].map(self.format_amount)

        # Ignore the rows that are not expenses (empty lines, totals...)
        df = df.dropna(subset=['date', 'value'])

        return [
            self.debug_expense(r)
             for _, r in df.iterrows()
        ]

    def find_xls_header_row(self, df):
        for index, value in enumerate(df.iloc[:, 0]):
            if str(value).strip().upper() == 'F. VALOR':
                return index

        raise ValueError('The header row (F. VALOR) has not been found in the xls file')

    def format_amount(self, value):
        if isinstance(value, str):
            # Spanish format: 1.234,56
            value = value.replace('€', '').replace('.', '').replace(',', '.').strip()

        return pd.to_numeric(value, errors='coerce')
    
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

    def format_nan(self, value):
        return None if pd.isna(value) else value
