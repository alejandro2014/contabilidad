from src.services.BaseService import BaseService

class RulesService(BaseService):
    def __init__(self):
        super().__init__()

    def add_rule(self, category, rule):
        if self.rule_exists(category, rule):
            print(f'Error: The rule "{rule}" in the category "{category}" already exists')
            return 1

        sql = self.sql_generator.insert_rule(category, rule)
        self.db.execute_sql(sql)

    def rule_exists(self, category, rule):
        sql = self.sql_generator.select_rule_count(category, rule)

        return self.get_single_value(sql) > 0

    def get_rules(self):
        sql = self.sql_generator.select_rules()

        return [ {
            'priority': r[0],
            'rule': r[1],
            'category': r[2]
        } for r in self.db.select(sql) ]

    def update_rule(self, priority, rule, category):
        sql = self.sql_generator.update_rule(priority, rule, category)
        self.db.execute_sql(sql)

    def delete_rule_by_priority(self, priority):
        sql = self.sql_generator.delete_rule_by_priority(priority)
        self.db.execute_sql(sql)

    def swap_priorities(self, priority_a, priority_b):
        # The priority is the primary key, so one of them has to be moved out of the way first
        temporary_priority = 0

        self.db.execute_sql(self.sql_generator.update_rule_priority(priority_a, temporary_priority))
        self.db.execute_sql(self.sql_generator.update_rule_priority(priority_b, priority_a))
        self.db.execute_sql(self.sql_generator.update_rule_priority(temporary_priority, priority_b))

    def find_rule_index(self, rules, concept):
        # Index of the first rule matched by the concept, or None
        concept = concept.lower()

        for index, rule in enumerate(rules):
            if rule['rule'].lower() in concept:
                return index

        return None

    def classify_expenses(self, expenses):
        rules = self.get_rules()

        for expense in expenses:
            if expense.category is None:
                expense.category = self.find_category(rules, expense.title)

    def find_category(self, rules, concept):
        # The rules are sorted by priority, so only the first match counts
        index = self.find_rule_index(rules, concept)

        return None if index is None else rules[index]['category']
