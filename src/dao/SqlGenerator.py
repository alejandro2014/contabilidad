class SqlGenerator:
    def insert_expense(self, expense):
        expense_values = expense.__dict__
        filtered_values = {}

        for k in expense_values.keys():
            if expense_values[k] is not None and k != 'class_name':
                filtered_values[k] = expense_values[k]

        fields = ', '.join([k for k in filtered_values.keys()])
        values = ', '.join([self.field_value(k) for k in filtered_values.values()])

        return f"INSERT INTO expenses ({fields}) VALUES ({values})"
    
    def select_pending_expenses(self, filter=None, sort_by=None):
        sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL)"

        return self.select_expenses(sql, filter, sort_by)
    
    def select_classified_expenses(self, filter=None, sort_by=None):
        sql = "SELECT id, date, title, amount, category FROM expenses WHERE (category IS NOT NULL)"

        return self.select_expenses(sql, filter, sort_by)
    
    def select_expenses(self, sql, filter=None, sort_by=None):
        if filter != None:
            date_from, date_to, search_value = self.get_filter_values(filter)

            if date_from != None and date_to != None:
                sql += f" AND (date BETWEEN '{date_from}' AND '{date_to}')"

            if search_value != None:
                sql += f" AND (title LIKE '%{search_value}%')"

        if sort_by != None:
            sql += f' ORDER BY {sort_by} ASC'

        return sql
    
    def get_filter_values(self, filter):
        date_from = filter['date']['from'] if 'date' in filter and 'from' in filter['date'] else None
        date_to = filter['date']['to'] if 'date' in filter and 'to' in filter['date'] else None
        search_value = filter['search_value'] if 'search_value' in filter else None

        return date_from, date_to, search_value
    
    def select_classified_expenses_count(self):
        return 'SELECT count(*) FROM expenses WHERE (category IS NOT NULL)'

    def select_classified_expenses_by_type(self):
        return "SELECT category, sum(amount) AS sum FROM expenses WHERE (category IS NOT NULL) GROUP BY category"

    def select_classified_expenses_by_month(self):
        return f"SELECT substr(date, 0, 7) AS month, sum(amount) AS sum FROM expenses WHERE (category IS NOT NULL) AND {self.computed_expense_condition()} GROUP BY month"
    
    def select_classified_expenses_by_type_and_month(self):
        return "SELECT category, substr(date, 0, 7) AS month, sum(amount) AS sum FROM expenses WHERE (category IS NOT NULL) GROUP BY category, month"
    
    def select_pending_expenses_count(self):
        return "SELECT count(*) FROM expenses WHERE (category IS NULL)"

    def select_expense_types_full(self):
        return "SELECT category, comment, income, not_computed FROM expense_types ORDER BY category"
    
    def select_not_computed_categories(self):
        return "SELECT category FROM expense_types WHERE income OR not_computed"

    def select_expense_types_simple(self):
        return "SELECT category FROM expense_types ORDER BY category"

    def delete_expense_type(self, category):
        return f"DELETE FROM expense_types WHERE category = '{category}'"
    
    def update_expense_type(self, old_category, old_comment, field, new_value):
        category_condition = 'category is NULL' if old_category == '' else f"category = '{old_category}'"
        comment_condition = 'comment is NULL' if old_comment == '' else f"comment = '{old_comment}'"

        return f"UPDATE expense_types SET {field} = '{new_value}' WHERE {category_condition} AND {comment_condition}"

    def update_expense_type_flag(self, category, flag, value):
        flag_value = self.bool_value(value)

        return f"UPDATE expense_types SET {flag} = {flag_value} WHERE category = '{category}'"

    def select_category_name(self, category):
        return f"SELECT count(*) FROM expense_types WHERE category = '{category}'"

    def insert_category(self, category_name, category_description, income=False, not_computed=False):
        income_value = self.bool_value(income)
        not_computed_value = self.bool_value(not_computed)

        return f"INSERT INTO expense_types(category, comment, income, not_computed) VALUES ('{category_name}', '{category_description}', {income_value}, {not_computed_value})"
    
    def update_classified_expense(self, expense_id, category):
        return f"UPDATE expenses set category = '{category}' WHERE id = '{expense_id}'"

    def update_unclassified_expense(self, expense_id):
        return f"UPDATE expenses set category = NULL WHERE id = '{expense_id}'"
    
    def bool_value(self, value):
        return 'TRUE' if value else 'FALSE'

    def field_value(self, field):
        return f"'{field}'" if type(field) == str else str(field)
    
    def computed_expense_condition(self):
        return "category NOT IN (SELECT category FROM expense_types WHERE income OR not_computed)"

    def select_rules(self):
        return "SELECT priority, rule, category FROM rules ORDER BY priority"

    def select_rule_count(self, category, rule):
        return f"SELECT count(*) FROM rules WHERE category = '{self.escape(category)}' AND rule = '{self.escape(rule)}'"

    def insert_rule(self, category, rule):
        # New rules go to the end of the list, with the lowest priority
        return f"INSERT INTO rules (priority, rule, category) VALUES ((SELECT COALESCE(MAX(priority), 0) + 1 FROM rules), '{self.escape(rule)}', '{self.escape(category)}')"

    def delete_rule_by_priority(self, priority):
        return f"DELETE FROM rules WHERE priority = {int(priority)}"

    def update_rule(self, priority, rule, category):
        return f"UPDATE rules SET rule = '{self.escape(rule)}', category = '{self.escape(category)}' WHERE priority = {int(priority)}"

    def update_rule_priority(self, old_priority, new_priority):
        return f"UPDATE rules SET priority = {int(new_priority)} WHERE priority = {int(old_priority)}"

    def escape(self, value):
        # The rules are typed by the user, so they can contain quotes
        return value.replace("'", "''")

    def select_cashflow(self, year, group_by):
        # The bank category comes with every expense, the expense type only once it is classified
        group_field = 'category_src' if group_by == 'bank' else "COALESCE(category, 'Sin clasificar')"
        income_field = "(category IS NOT NULL AND category IN (SELECT category FROM expense_types WHERE income))"
        not_computed_condition = "(category IS NULL OR category NOT IN (SELECT category FROM expense_types WHERE not_computed))"

        return f"SELECT {income_field} AS is_income, {group_field} AS grp, CAST(substr(date, 5, 2) AS INTEGER) AS month, sum(amount) FROM expenses WHERE date LIKE '{year}%' AND {not_computed_condition} GROUP BY is_income, grp, month"

    def select_pie_chart_categories(self, params):
        date_from = params['date_from']
        date_to = params['date_to']

        return f"SELECT category, sum(amount) AS amnt FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND date BETWEEN '{date_from}' AND '{date_to}' GROUP BY category ORDER BY abs(amnt) DESC"
    
    def select_bar_chart_values(self, params):
        date_from = params['date_from']
        date_to = params['date_to']

        return f"SELECT SUBSTR(date, 1, 6) AS d, SUM(amount) FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND date BETWEEN '{date_from}' AND '{date_to}' GROUP BY d"
    def select_income_chart_values(self, params):
        date_from = params['date_from']
        date_to = params['date_to']

        return f"SELECT SUBSTR(date, 1, 6) AS d, SUM(amount) FROM expenses WHERE category IN (SELECT category FROM expense_types WHERE income) AND date BETWEEN '{date_from}' AND '{date_to}' GROUP BY d"

    def select_category_month_values(self, params):
        date_from = params['date_from']
        date_to = params['date_to']

        return f"SELECT category, SUBSTR(date, 1, 6) AS d, SUM(amount) FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND date BETWEEN '{date_from}' AND '{date_to}' GROUP BY category, d"

    def select_top_expenses(self, params, limit):
        date_from = params['date_from']
        date_to = params['date_to']

        # The biggest expenses are the most negative amounts. The repeated ones (same concept and amount, like the rent) are a single row
        return f"SELECT MIN(date), MAX(date), title, category, amount, count(*) FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND amount < 0 AND date BETWEEN '{date_from}' AND '{date_to}' GROUP BY title, category, amount ORDER BY amount ASC LIMIT {int(limit)}"

    def select_pending_expenses_count_between(self, params):
        date_from = params['date_from']
        date_to = params['date_to']

        return f"SELECT count(*) FROM expenses WHERE (category IS NULL) AND date BETWEEN '{date_from}' AND '{date_to}'"
