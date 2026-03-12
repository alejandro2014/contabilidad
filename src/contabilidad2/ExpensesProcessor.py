import json
import re

class ExpensesProcessor:
    def __init__(self, rules='./rules.json'):
        self._rules_file = rules

    def process_expenses(self, expense_lines):
        rules = self.get_rules()

        expenses = self.process_lines(expense_lines, rules)

        return expenses

    def process_lines(self, expense_lines, rules):
        expenses = []

        for line in expense_lines:
            line['category1'] = self.get_category(line, rules)

            expenses.append(line)

        return expenses

    def get_category(self, line, rules):
        for category in rules['categories']:
            for rule in category['rules']:
                if re.match(f'.*{rule}.*', line['concept']):
                    return category['name']

        return None

    def get_rules(self):
        with open(self._rules_file, 'r') as f:
            rules = json.load(f)

        return rules
