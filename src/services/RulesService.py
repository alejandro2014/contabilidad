from CsvReader import CsvReader

from src.dao.RulesDao import RulesDao

class RulesService:
    def __init__(self):
        self.rules_dao = RulesDao()

        self._csv_reader = CsvReader(self.get_line_transform())

    def add_rule(self, category, rule):
        rule_exists = self.rules_dao.rule_exists(category, rule)

        if rule_exists:
            print(f'Error: The rule "{rule}" in the category "{category}" already exists')
            return 1

        self.rules_dao.add_rule(category, rule)

    def delete_rule(self, category, rule):
        rule_exists = self.rules_dao.rule_exists(category, rule)

        if not rule_exists:
            print(f'Error: The rule "{rule}" in the category "{category}" does not exist')
            return 1

        self.rules_dao.delete_rule(category, rule)

    def get_rules(self):
        return self.rules_dao.get_rules()

    def import_rules(self, file_path):
        rules, _ = self._csv_reader.read_file(file_path)

        for r in rules:
            category = r['category']
            rule = r['rule']

            self.rules_dao.add_rule(category, rule)

    def get_line_transform(self):
        return lambda l: {
            'category': l[0],
            'rule': l[1]
        }

    def export_rules(self, file_path):
        rules = self.rules_dao.get_rules()

        with open(file_path, 'w') as f:
            for r in rules:
                line = f'{r["category"]}\t{r["rule"]}\n'
                f.write(line)
