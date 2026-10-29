class SqlGenerator:
    # Every query with values returns (sql, params): the values always go as parameters (?), never inside the sql

    # Columns of the expenses tables that can be used to sort (the "field"s of the table configs, as they are in the database)
    SORTABLE_COLUMNS = { 'date': 'date', 'concept': 'title', 'title': 'title', 'quantity': 'amount', 'amount': 'amount', 'type': 'category', 'category': 'category' }

    EXPENSE_COLUMNS = [ 'id', 'date', 'category_src', 'subcategory_src', 'title', 'amount', 'category', 'subcategory', 'category_suggested', 'subcategory_suggested' ]

    def insert_expenses(self):
        # The movements already loaded (same date, concept and amount) are ignored
        fields = ', '.join(self.EXPENSE_COLUMNS)
        values = ', '.join([ '?' for _ in self.EXPENSE_COLUMNS ])

        return f"INSERT OR IGNORE INTO expenses ({fields}) VALUES ({values})"

    def expense_values(self, expense):
        return tuple(getattr(expense, c) for c in self.EXPENSE_COLUMNS)

    def select_pending_expenses(self, filter=None, sort_by=None):
        sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL)"

        return self.select_expenses(sql, filter, sort_by)

    def select_classified_expenses(self, filter=None, sort_by=None):
        sql = "SELECT id, date, title, amount, category FROM expenses WHERE (category IS NOT NULL)"

        return self.select_expenses(sql, filter, sort_by)

    def select_expenses(self, sql, filter=None, sort_by=None):
        params = []

        if filter != None:
            date_from, date_to, search_value = self.get_filter_values(filter)
            amount_from, amount_to, category = self.get_search_values(filter)

            if date_from != None and date_to != None:
                sql += " AND (date BETWEEN ? AND ?)"
                params += [ date_from, date_to ]

            if search_value != None:
                sql += " AND (title LIKE ?)"
                params.append(f'%{search_value}%')

            # Expenses are stored as negative amounts, but they are searched by how much they are
            if amount_from != None:
                sql += " AND (ROUND(ABS(amount), 2) >= ?)"
                params.append(float(amount_from))

            if amount_to != None:
                sql += " AND (ROUND(ABS(amount), 2) <= ?)"
                params.append(float(amount_to))

            if category != None:
                sql += " AND (category = ?)"
                params.append(category)

        if sort_by != None:
            sql += f' ORDER BY {self.sort_column(sort_by)} ASC'

        return sql, tuple(params)

    def sort_column(self, sort_by):
        # A column name can't be a parameter, so only the known ones are accepted
        if sort_by not in self.SORTABLE_COLUMNS:
            raise ValueError(f'The expenses can not be sorted by "{sort_by}"')

        return self.SORTABLE_COLUMNS[sort_by]

    def get_filter_values(self, filter):
        date_from = filter['date']['from'] if 'date' in filter and 'from' in filter['date'] else None
        date_to = filter['date']['to'] if 'date' in filter and 'to' in filter['date'] else None
        search_value = filter['search_value'] if 'search_value' in filter else None

        return date_from, date_to, search_value

    def get_search_values(self, filter):
        amount_from = filter['amount']['from'] if 'amount' in filter and 'from' in filter['amount'] else None
        amount_to = filter['amount']['to'] if 'amount' in filter and 'to' in filter['amount'] else None
        category = filter['category'] if 'category' in filter else None

        return amount_from, amount_to, category

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

    def select_expenses_date_range(self):
        return "SELECT (category IS NOT NULL) AS classified, MIN(date), MAX(date), count(*) FROM expenses GROUP BY classified"

    def select_expense_types_full(self):
        return "SELECT category, comment, income, not_computed FROM expense_types ORDER BY category"

    def select_not_computed_categories(self):
        return "SELECT category FROM expense_types WHERE income OR not_computed"

    def select_expense_types_simple(self):
        return "SELECT category FROM expense_types ORDER BY category"

    def select_expense_type_usage(self, category):
        return "SELECT (SELECT count(*) FROM expenses WHERE category = ?), (SELECT count(*) FROM rules WHERE category = ?)", (category, category)

    def delete_expense_type(self, category):
        return "DELETE FROM expense_types WHERE category = ?", (category,)

    def move_expenses_to_type(self, old_category, new_category):
        # new_category None leaves the expenses pending again
        return "UPDATE expenses SET category = ? WHERE category = ?", (new_category, old_category)

    def move_rules_to_type(self, old_category, new_category):
        return "UPDATE rules SET category = ? WHERE category = ?", (new_category, old_category)

    def delete_rules_of_type(self, category):
        return "DELETE FROM rules WHERE category = ?", (category,)

    def rename_expense_type(self, old_category, new_category):
        return "UPDATE expense_types SET category = ? WHERE category = ?", (new_category, old_category)

    def update_expense_type_comment(self, category, comment):
        return "UPDATE expense_types SET comment = ? WHERE category = ?", (comment, category)

    def update_expense_type_flag(self, category, flag, value):
        # A column name can't be a parameter, so only the flags are accepted
        if flag not in ('income', 'not_computed'):
            raise ValueError(f'"{flag}" is not a flag of the expense types')

        return f"UPDATE expense_types SET {flag} = ? WHERE category = ?", (bool(value), category)

    def select_category_name(self, category):
        return "SELECT count(*) FROM expense_types WHERE category = ?", (category,)

    def insert_category(self, category_name, category_description, income=False, not_computed=False):
        return "INSERT INTO expense_types(category, comment, income, not_computed) VALUES (?, ?, ?, ?)", (category_name, category_description, bool(income), bool(not_computed))

    def update_classified_expense(self, expense_id, category):
        return "UPDATE expenses set category = ? WHERE id = ?", (category, expense_id)

    def update_unclassified_expense(self, expense_id):
        return "UPDATE expenses set category = NULL WHERE id = ?", (expense_id,)

    def computed_expense_condition(self):
        return "category NOT IN (SELECT category FROM expense_types WHERE income OR not_computed)"

    def select_rules(self):
        return "SELECT priority, rule, category FROM rules ORDER BY priority"

    def select_rule_count(self, category, rule):
        return "SELECT count(*) FROM rules WHERE category = ? AND rule = ?", (category, rule)

    def insert_rule(self, category, rule):
        # New rules go to the end of the list, with the lowest priority
        return "INSERT INTO rules (priority, rule, category) VALUES ((SELECT COALESCE(MAX(priority), 0) + 1 FROM rules), ?, ?)", (rule, category)

    def delete_rule_by_priority(self, priority):
        return "DELETE FROM rules WHERE priority = ?", (int(priority),)

    def update_rule(self, priority, rule, category):
        return "UPDATE rules SET rule = ?, category = ? WHERE priority = ?", (rule, category, int(priority))

    def update_rule_priority(self, old_priority, new_priority):
        return "UPDATE rules SET priority = ? WHERE priority = ?", (int(new_priority), int(old_priority))

    def select_cashflow(self, year, group_by):
        # The bank category comes with every expense, the expense type only once it is classified
        group_field = 'category_src' if group_by == 'bank' else "COALESCE(category, 'Sin clasificar')"
        income_field = "(category IS NOT NULL AND category IN (SELECT category FROM expense_types WHERE income))"
        not_computed_condition = "(category IS NULL OR category NOT IN (SELECT category FROM expense_types WHERE not_computed))"

        return f"SELECT {income_field} AS is_income, {group_field} AS grp, CAST(substr(date, 5, 2) AS INTEGER) AS month, sum(amount) FROM expenses WHERE date LIKE ? AND {not_computed_condition} GROUP BY is_income, grp, month", (f'{year}%',)

    def date_params(self, params):
        return (params['date_from'], params['date_to'])

    def select_pie_chart_categories(self, params):
        return f"SELECT category, sum(amount) AS amnt FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND date BETWEEN ? AND ? GROUP BY category ORDER BY abs(amnt) DESC", self.date_params(params)

    def select_category_titles(self, params, category):
        return "SELECT title, sum(amount) FROM expenses WHERE category = ? AND date BETWEEN ? AND ? GROUP BY title", (category,) + self.date_params(params)

    def select_bar_chart_values(self, params):
        return f"SELECT SUBSTR(date, 1, 6) AS d, SUM(amount) FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND date BETWEEN ? AND ? GROUP BY d", self.date_params(params)

    def select_income_chart_values(self, params):
        return "SELECT SUBSTR(date, 1, 6) AS d, SUM(amount) FROM expenses WHERE category IN (SELECT category FROM expense_types WHERE income) AND date BETWEEN ? AND ? GROUP BY d", self.date_params(params)

    def select_category_month_values(self, params):
        return f"SELECT category, SUBSTR(date, 1, 6) AS d, SUM(amount) FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND date BETWEEN ? AND ? GROUP BY category, d", self.date_params(params)

    def select_top_expenses(self, params, limit):
        # The biggest expenses are the most negative amounts. The repeated ones (same concept and amount, like the rent) are a single row
        return f"SELECT MIN(date), MAX(date), title, category, amount, count(*) FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND amount < 0 AND date BETWEEN ? AND ? GROUP BY title, category, amount ORDER BY amount ASC LIMIT ?", self.date_params(params) + (int(limit),)

    def select_pending_expenses_count_between(self, params):
        return "SELECT count(*) FROM expenses WHERE (category IS NULL) AND date BETWEEN ? AND ?", self.date_params(params)
