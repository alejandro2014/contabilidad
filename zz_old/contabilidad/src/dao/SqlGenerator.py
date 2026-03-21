from src.config.ConfigLoader import ConfigLoader
from src.dao.base_sql_generator import BaseSqlGenerator

class SqlGenerator(BaseSqlGenerator):
    def __init__(self, excl_categories):
        super(SqlGenerator, self).__init__(excl_categories)
        self.queries_info = ConfigLoader().load_config_file('db/queries-info')

    def insert_pending_expense(self, concept_line):
        query_info = self.get_query_info(self.queries_info, 'insert_pending_expense')

        return self.compose_insert(query_info, concept_line)

    def insert_classified_expense(self, expense):
        expense_data = expense['expense_data']
        expense_data['category'] = expense['category']

        query_info = self.get_query_info(self.queries_info, 'insert_classified_expense')

        return self.compose_insert(query_info, expense_data)

    def select_pending_expenses(self, filter = None):
        query_info = self.get_query_info(self.queries_info, 'select_pending_expenses')

        sql = self.compose_select(query_info)

        return self.select_expenses(sql, filter)

    def select_classified_expenses(self, filter = None):
        query_info = self.get_query_info(self.queries_info, 'select_classified_expenses')

        query_info['where'] = f'{self.exclusions()}'

        sql = self.compose_select(query_info)

        return self.select_expenses(sql, filter)

    def select_expenses(self, sql, filter = None):
        if filter == None:
            return sql

        date_from = self.value('date.from', filter)
        date_to = self.value('date.to', filter)
        search_value = self.value('search_value', filter)

        if date_from != None and date_to != None:
            sql += f" AND (date_record BETWEEN '{date_from}' AND '{date_to}')"

        if search_value != None:
            sql += f" AND (concept LIKE '%{search_value}%')"

        return sql

    def delete_pending_expense(self, expense):
        query_info = self.get_query_info(self.queries_info, 'delete_pending_expense')

        return self.compose_delete(query_info, expense)

    def select_classified_expenses_count(self):
        query_info = self.get_query_info(self.queries_info, 'select_classified_expenses_count')

        query_info['where'] = f'{self.exclusions()}'

        return self.compose_select(query_info)

    def select_classified_expenses_by_type(self):
        query_info = self.get_query_info(self.queries_info, 'select_classified_expenses_by_type')

        query_info['where'] = f'{self.exclusions()}'

        sql = self.compose_select(query_info)

        return f"{sql} group by type"

    def select_classified_expenses_by_month(self):
        query_info = self.get_query_info(self.queries_info, 'select_classified_expenses_by_month')

        query_info['where'] = f'{self.exclusions()}'

        sql = self.compose_select(query_info)

        return f"{sql} group by month"

    def select_classified_expenses_by_type_and_month(self):
        query_info = self.get_query_info(self.queries_info, 'select_classified_expenses_by_type_and_month')

        query_info['where'] = f'{self.exclusions()}'

        sql = self.compose_select(query_info)

        return f"{sql} group by type, month"

    def select_pending_expenses_count(self):
        query_info = self.get_query_info(self.queries_info, 'select_pending_expenses_count')

        return self.compose_select(query_info)

    def select_expense_types_count(self):
        query_info = self.get_query_info(self.queries_info, 'select_expense_types_count')

        return self.compose_select(query_info)

    def select_expense_types_full(self):
        query_info = self.get_query_info(self.queries_info, 'select_expense_types_full')

        sql = self.compose_select(query_info)

        return f'{sql} ORDER BY category'

    def select_expense_types_names(self):
        query_info = self.get_query_info(self.queries_info, 'select_expense_types_names')

        sql = self.compose_select(query_info)

        return f'{sql} ORDER BY category'

    def delete_expense_type(self, category):
        query_info = self.get_query_info(self.queries_info, 'delete_expense_type')

        return self.compose_delete(query_info, category)

    def select_category_name(self, category_name):
        query_info = self.get_query_info(self.queries_info, 'select_category_name')

        query_info['where'] = f"category = '{category_name}'"

        return self.compose_select(query_info)

    def insert_category(self, category):
        query_info = self.get_query_info(self.queries_info, 'insert_category')

        return self.compose_insert(query_info, category)
