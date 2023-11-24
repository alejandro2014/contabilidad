from dao.SqliteConnector import SqliteConnector

class RulesDao:
    def __init__(self):
        self._db = SqliteConnector()

    def add_rule(self, category, rule):
        sql = (
            f"INSERT INTO rules (category, rule) "
            f"VALUES ('{category}', '{rule}')"
        )

        self._db.insert(sql)

    def delete_rule(self, category, rule):
        sql = (
            f"DELETE FROM rules WHERE "
            f"category = '{category}' AND rule = '{rule}'"
        )

        self._db.delete(sql)

    def rule_exists(self, category, rule):
        sql = f"SELECT COUNT(*) FROM rules WHERE category = '{category}' AND rule = '{rule}'"

        raw_result = self._db.select(sql)

        return raw_result[0][0] > 0

    def get_rules(self):
        sql = f"SELECT category, rule FROM rules ORDER BY category, rule"

        raw_result = self._db.select(sql)

        return [{
            'category': r[0],
            'rule': r[1]
        } for r in raw_result]
