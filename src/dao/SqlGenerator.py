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

    def field_value(self, field):
        return f"'{field}'" if type(field) == str else str(field)
    
    def insert_pending_expense(self, concept_line):
        date_record = concept_line['date']
        concept = concept_line['concept']
        category = concept_line['category']
        subcategory = concept_line['subcategory']
        quantity = concept_line['value']

        return f"INSERT INTO expenses_not_classified (date_record, concept, category, subcategory, quantity) \
            VALUES ('{date_record}', '{concept}', '{category}', '{subcategory}', {quantity})"
    
    #-----------------------------------------------------------
    def select_pending_expenses(self, filter=None, sort_by=None):
        sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NULL)"

        return self.select_expenses(sql, filter, sort_by)
    
    def select_classified_expenses(self, filter=None, sort_by=None):
        sql = "SELECT id, date, title, amount FROM expenses WHERE (category IS NOT NULL)"

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
    
    def delete_pending_expense(self, expense):
        date_record = expense['date']
        title = expense['title']
        amount = expense['amount']

        return f"DELETE FROM expenses WHERE date = '{date_record}' AND title = '{title}' AND amount = {amount}"
    
    def select_classified_expenses_count(self):
        return 'SELECT count(*) FROM expenses WHERE (category IS NOT NULL)'

    def select_classified_expenses_by_type(self):
        return "SELECT type, sum(amount) AS sum FROM expenses WHERE (category IS NOT NULL) GROUP BY type"

    def select_classified_expenses_by_month(self):
        # TODO Consider the savings account as well
        return "SELECT substr(date, 0, 7) AS month, sum(amount) AS sum FROM expenses (category IS NOT NULL) GROUP BY month"
    
    def select_classified_expenses_by_type_and_month(self):
        return "SELECT type, substr(date, 0, 7) AS month, sum(quantity) AS sum FROM expenses (category IS NOT NULL) group by type, month"
    
    def select_pending_expenses_count(self):
        return "SELECT count(*) FROM expenses WHERE (category IS NULL)"

    def select_expense_types_full(self):
        return "SELECT category, comment FROM expense_types ORDER BY category"

    def delete_expense_type(self, category):
        return f"DELETE FROM expense_types WHERE category = '{category}'"

    def select_category_name(self, category):
        return f"SELECT count(*) FROM expense_types WHERE category = '{category}'"

    def insert_category(self, category_name, category_description):
        return f"INSERT INTO expense_types(category, comment) VALUES ('{category_name}', '{category_description}')"
    
    def update_classified_expense(self, expense_id, category):
        return f"UPDATE expenses set category = '{category}' WHERE id = '{expense_id}'"
