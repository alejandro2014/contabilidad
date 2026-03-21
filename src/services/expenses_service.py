import re

from src.dao.expenses_dao import ExpensesDao
from src.dao.rules_dao import RulesDao
from src.dao.sqlite_connector import SqliteConnector


class ExpensesService:
    def __init__(self):
        self._expenses_dao = ExpensesDao(SqliteConnector())
        self._rules_dao = RulesDao(SqliteConnector())

    def get_expenses(self, args):
        return self._expenses_dao.get_expenses(
            expense_type = args.expense_type,
            ids = args.ids,
            file_hash = args.file_hash,
            search = args.search,
            date = args.date,
            date_from = args.date_from,
            date_to = args.date_to,
            condition = args.condition
        )

    def load_expenses(self, expenses, hash):
        for i, expense in enumerate(expenses):
            expense['hash'] = hash
            expense['id'] = f'{hash}-{str(i).zfill(4)}'
            expense['date'] = self.convert_date(expense['date'])

            self._expenses_dao.load_expense(expense)

    def load_expense(self, expense):
        self._expenses_dao.load_expense(expense)

    def delete_expenses(self, hash_file):
        self._expenses_dao.delete_expenses(hash_file)

    def classify_expenses(self, expenses=None, expense_type='unclassified'):
        if expenses is None:
            expenses = self._expenses_dao.get_expenses(expense_type=expense_type)

        rules = self._rules_dao.get_rules()

        expenses = self.process_lines(expenses, rules)

        for expense in expenses:
            if 'category1' in expense and expense['category1'] is not None and 'id' in expense:
                category = expense['category1']
                expense_id = expense['id']
                self._expenses_dao.update_category(expense_id, category)

        return expenses

    def unclassify_expenses(self, ids=None, file_hash=None, search=None,
                            date=None, date_from=None, date_to=None,
                            condition=None):
        if ids is not None:
            ids_list = ids.split(',')

            for id in ids_list:
                self._expenses_dao.unclassify_by_id(id)

            return

        if file_hash is not None:
            self._expenses_dao.unclassify_by_file_hash(file_hash, search, condition)
            return

        if date is not None:
            self._expenses_dao.unclassify_by_date_and_search(date, search, condition)
            return

        if date_from is not None or date_to is not None:
            self._expenses_dao.unclassify_by_dates_fromto_and_search(date_from, date_to, search, condition)
            return

        self._expenses_dao.unclassify_by_search_and_condition(search, condition)

    def process_lines(self, expenses_input, rules):
        expenses_output = []

        for expense in expenses_input:
            category = self.get_category(expense, rules)

            if category is not None:
                expense['category1'] = self.get_category(expense, rules)

            expenses_output.append(expense)

        return expenses_output

    def get_category(self, expense, rules):
        for rule in rules:
            if re.match(f'.*{rule["rule"]}.*', expense['concept']):
                return rule['category']

        return None

    def convert_date(self, date_input):
        day = date_input[0:2]
        month = date_input[3:5]
        year = date_input[6:10]

        return f'{year}{month}{day}'
    
    def get_pending_expenses_count(self):
        return self._expenses_dao.get_pending_expenses_count()

    def get_classified_expenses_count(self):
        return self._expenses_dao.get_classified_expenses_count()
