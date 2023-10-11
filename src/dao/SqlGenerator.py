class SqlGenerator:
    def insert_pending_expense(self, concept_line):
        date_record = concept_line['date']
        concept = concept_line['concept']
        category = concept_line['category']
        subcategory = concept_line['subcategory']
        quantity = concept_line['value']

        return f"INSERT INTO expenses_not_classified (date_record, concept, category, subcategory, quantity) \
            VALUES ('{date_record}', '{concept}', '{category}', '{subcategory}', {quantity})"

    def insert_classified_expense(self, expense, category):
        date_record = expense['date']
        concept = expense['concept']
        quantity = expense['quantity']

        return "INSERT INTO expenses_classified (date_record, concept, quantity, type) VALUES ('" + date_record + "', '" + concept + "', " + quantity + ", '" + category + "')"

    def select_pending_expenses(self, filter = None):
        sql = "SELECT date_record, concept, quantity FROM expenses_not_classified WHERE (1 = 1)"

        if filter == None:
            return sql

        date_from = filter['date']['from'] if 'date' in filter and 'from' in filter['date'] else None
        date_to = filter['date']['to'] if 'date' in filter and 'to' in filter['date'] else None
        search_value = filter['search_value'] if 'search_value' in filter else None

        if date_from != None and date_to != None:
            sql += " AND (date_record BETWEEN '" + date_from + "' AND '" + date_to + "')"

        if search_value != None:
            sql += " AND (concept LIKE '%" + search_value + "%')"

        return sql

    def select_classified_expenses(self, filter = None):
        sql = "SELECT date_record, concept, type, quantity FROM expenses_classified WHERE (1 = 1)"

        if filter == None:
            return sql

        date_from = filter['date']['from'] if 'date' in filter and 'from' in filter['date'] else None
        date_to = filter['date']['to'] if 'date' in filter and 'to' in filter['date'] else None
        search_value = filter['search_value'] if 'search_value' in filter else None

        if date_from != None and date_to != None:
            sql += " AND (date_record BETWEEN '" + date_from + "' AND '" + date_to + "')"

        if search_value != None:
            sql += " AND (concept LIKE '%" + search_value + "%')"

        return sql

    def delete_pending_expense(self, expense):
        date_record = expense['date']
        concept = expense['concept']
        quantity = expense['quantity']

        return "DELETE FROM expenses_not_classified WHERE date_record = '" + date_record + "' AND concept = '" + concept + "' AND quantity = " + quantity

    def select_classified_expenses_count(self):
        return 'SELECT count(*) FROM expenses_classified'

    def select_classified_expenses_by_type(self):
        return 'select type, sum(quantity) as sum from expenses_classified group by type'

    def select_classified_expenses_by_month(self):
        #TODO Consider the savings account as well
        return "select substr(date_record, 0, 7) as month, sum(quantity) as sum from expenses_classified group by month"

    def select_classified_expenses_by_type_and_month(self):
        return 'select type, substr(date_record, 0, 7) as month, sum(quantity) as sum from expenses_classified group by type, month'

    def select_pending_expenses_count(self):
        return 'SELECT count(*) FROM expenses_not_classified'

    def select_expense_types_full(self):
        return 'select category, comment from expense_types ORDER BY category'

    def delete_expense_type(self, category):
        return f"delete from expense_types where category = '{category}'"

    def select_category_name(self, category_name):
        return f"select count(*) from expense_types where category = '{category_name}'"

    def insert_category(self, category_name, category_description):
        return f"INSERT INTO expense_types(category, comment) VALUES ('{category_name}', '{category_description}')"
