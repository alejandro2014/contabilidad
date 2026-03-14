from src.model.Rule import Rule

class RulesDao:
    def __init__(self, db_connector):
        self._db = db_connector

    def add_rule(self, rule):
        sql = "INSERT INTO rules (category, rule) VALUES (?, ?)"
        params = (
            rule.category,
            rule.rule
        )

        self._db.run_sql(sql, params)

    def delete_rule(self, rule):
        sql = "DELETE FROM rules WHERE category = ? AND rule = ?"
        params = (
            rule.category,
            rule.rule
        ) 

        self._db.run_sql(sql, params)

    def rule_exists(self, rule):
        sql = "SELECT COUNT(*) FROM rules WHERE category = ? AND rule = ?"
        params = (
            rule.category,
            rule.rule
        )

        raw_result = self._db.run_sql(sql, params)

        return raw_result[0][0] > 0

    def get_rules(self):
        sql = f"SELECT category, rule FROM rules ORDER BY category, rule"

        raw_result = self._db.select(sql)

        return [
            Rule(
                category=r[0],
                rule=r[1]
            ) for r in raw_result
        ]
