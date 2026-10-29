class SqlGenerator:
    # Every query with values returns (sql, params): the values always go as parameters (?), never inside the sql

    # Columns of the expenses tables that can be used to sort (the "field"s of the table configs, as they are in the database)
    SORTABLE_COLUMNS = { 'date': 'date', 'concept': 'title', 'title': 'title', 'quantity': 'amount', 'amount': 'amount', 'type': 'category', 'category': 'category' }

    EXPENSE_COLUMNS = [ 'id', 'date', 'category_src', 'subcategory_src', 'title', 'amount', 'category', 'balance' ]

    # Separator of the tags of a movement when they come in a single column, so a tag can't have it
    TAGS_SEPARATOR = ','

    def insert_expenses(self):
        # The movements already loaded (same date, concept and amount) are ignored, but they get the balance when
        # they were loaded before it was stored
        fields = ', '.join(self.EXPENSE_COLUMNS)
        values = ', '.join([ '?' for _ in self.EXPENSE_COLUMNS ])

        return f"INSERT INTO expenses ({fields}) VALUES ({values}) ON CONFLICT (date, title, amount) DO UPDATE SET balance = excluded.balance WHERE expenses.balance IS NULL"

    def expense_values(self, expense):
        return tuple(self.cents_or_none(getattr(expense, c)) if c in ('amount', 'balance') else getattr(expense, c) for c in self.EXPENSE_COLUMNS)

    def cents_or_none(self, amount):
        return None if amount is None else self.cents(amount)

    def cents(self, amount):
        # The amounts are stored as integer cents, so the sums are exact. The queries return them in euros (amount / 100.0)
        return int(round(float(amount) * 100))

    def select_pending_expenses(self, filter=None, sort_by=None):
        sql = "SELECT id, date, title, amount / 100.0 FROM expenses WHERE (category IS NULL)"

        return self.select_expenses(sql, filter, sort_by)

    def select_classified_expenses(self, filter=None, sort_by=None):
        sql = f"SELECT id, date, title, amount / 100.0, category, note, {self.tags_column()} FROM expenses WHERE (category IS NOT NULL)"

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
                sql += " AND (ABS(amount) >= ?)"
                params.append(self.cents(amount_from))

            if amount_to != None:
                sql += " AND (ABS(amount) <= ?)"
                params.append(self.cents(amount_to))

            if category != None:
                sql += " AND (category = ?)"
                params.append(category)

            tag = filter.get('tag')

            if tag != None:
                sql += " AND (id IN (SELECT expense_id FROM expense_tags WHERE tag = ?))"
                params.append(tag)

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

    def tags_column(self):
        return f"(SELECT group_concat(tag, '{self.TAGS_SEPARATOR}') FROM expense_tags WHERE expense_id = expenses.id) AS tags"

    def select_expenses_count(self):
        return 'SELECT count(*) FROM expenses'

    def select_classified_expenses_count(self):
        return 'SELECT count(*) FROM expenses WHERE (category IS NOT NULL)'

    def select_classified_expenses_by_type(self):
        return "SELECT category, sum(amount) / 100.0 AS sum FROM expenses WHERE (category IS NOT NULL) GROUP BY category"

    def select_classified_expenses_by_month(self):
        return f"SELECT substr(date, 1, 6) AS month, sum(amount) / 100.0 AS sum FROM expenses WHERE (category IS NOT NULL) AND {self.computed_expense_condition()} GROUP BY month"

    def select_classified_expenses_by_type_and_month(self):
        return "SELECT category, substr(date, 1, 6) AS month, sum(amount) / 100.0 AS sum FROM expenses WHERE (category IS NOT NULL) GROUP BY category, month"

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
        return "UPDATE expenses SET category = ? WHERE category = ?", (new_category, old_category)

    def move_rules_to_type(self, old_category, new_category):
        return "UPDATE rules SET category = ? WHERE category = ?", (new_category, old_category)

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

    def update_expense_note(self, expense_id, note):
        return "UPDATE expenses SET note = ? WHERE id = ?", (note, expense_id)

    def delete_expense_tags(self, expense_id):
        return "DELETE FROM expense_tags WHERE expense_id = ?", (expense_id,)

    def insert_expense_tag(self, expense_id, tag):
        return "INSERT OR IGNORE INTO expense_tags (expense_id, tag) VALUES (?, ?)", (expense_id, tag)

    def select_tags(self):
        return "SELECT DISTINCT tag FROM expense_tags ORDER BY tag"

    def select_tag_totals(self, filter):
        # Totals of what has been spent, so the incomes and the not computed types are left out like in the dashboard
        sql = f"SELECT t.tag, sum(e.amount) / 100.0, count(*) FROM expense_tags t JOIN expenses e ON e.id = t.expense_id WHERE (e.category IS NOT NULL) AND e.{self.computed_expense_condition()}"
        params = ()

        date_from, date_to, search_value = self.get_filter_values(filter or {})

        if date_from != None and date_to != None:
            sql += " AND (e.date BETWEEN ? AND ?)"
            params = (date_from, date_to)

        return sql + " GROUP BY t.tag ORDER BY t.tag", params

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

        return f"SELECT {income_field} AS is_income, {group_field} AS grp, CAST(substr(date, 5, 2) AS INTEGER) AS month, sum(amount) / 100.0 FROM expenses WHERE date LIKE ? AND {not_computed_condition} GROUP BY is_income, grp, month", (f'{year}%',)

    def date_params(self, params):
        return (params['date_from'], params['date_to'])

    def select_pie_chart_categories(self, params):
        return f"SELECT category, sum(amount) / 100.0 AS amnt FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND date BETWEEN ? AND ? GROUP BY category ORDER BY abs(amnt) DESC", self.date_params(params)

    def select_category_titles(self, params, category):
        return "SELECT title, sum(amount) / 100.0 FROM expenses WHERE category = ? AND date BETWEEN ? AND ? GROUP BY title", (category,) + self.date_params(params)

    def select_bar_chart_values(self, params):
        return f"SELECT SUBSTR(date, 1, 6) AS d, SUM(amount) / 100.0 FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND date BETWEEN ? AND ? GROUP BY d", self.date_params(params)

    def select_income_chart_values(self, params):
        return "SELECT SUBSTR(date, 1, 6) AS d, SUM(amount) / 100.0 FROM expenses WHERE category IN (SELECT category FROM expense_types WHERE income) AND date BETWEEN ? AND ? GROUP BY d", self.date_params(params)

    def select_category_month_values(self, params):
        return f"SELECT category, SUBSTR(date, 1, 6) AS d, SUM(amount) / 100.0 FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND date BETWEEN ? AND ? GROUP BY category, d", self.date_params(params)

    def select_top_expenses(self, params, limit):
        # The biggest expenses are the most negative amounts. The repeated ones (same concept and amount, like the rent) are a single row
        return f"SELECT MIN(date), MAX(date), title, category, amount / 100.0, count(*) FROM expenses WHERE category IS NOT NULL AND {self.computed_expense_condition()} AND amount < 0 AND date BETWEEN ? AND ? GROUP BY title, category, amount ORDER BY amount ASC LIMIT ?", self.date_params(params) + (int(limit),)

    def select_pending_expenses_count_between(self, params):
        return "SELECT count(*) FROM expenses WHERE (category IS NULL) AND date BETWEEN ? AND ?", self.date_params(params)

    def select_balances(self, params):
        # Every movement with the balance it left, to know the balance at the end of each month. The ones before the
        # range give the balance of its first months
        return "SELECT date, amount / 100.0, balance / 100.0 FROM expenses WHERE balance IS NOT NULL AND date <= ? ORDER BY date", (params['date_to'],)
