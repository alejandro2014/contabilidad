class KeyGetter:
    def value(self, key, object):
        split_key = key.split('.')

        for key_part in split_key:
            if not key_part in object:
                return None

            object = object[key_part]

        return object

class BaseSqlGenerator(KeyGetter):
    def __init__(self, excl_categories):
        self.excluded_column = 'type'

        self.excl_categories = excl_categories

        self.excl_incomes = self.excl_categories['incomes']
        self.excl_savings = self.excl_categories['savings']
        self.excl = self.excl_incomes + self.excl_savings

        self.print_query_info_flag = False

    def compose_delete(self, delete_info, data):
        table = delete_info['table']
        values = self.get_delete_values(delete_info, data)

        return f"DELETE FROM {table} WHERE {values}"

    def compose_insert(self, insert_info, data):
        table = insert_info['table']
        fields = ', '.join(insert_info['mappings'].keys())
        values = self.get_insert_values(insert_info, data)

        return f"INSERT INTO {table} ({fields}) VALUES ({values})"

    def get_insert_values(self, insert_info, data):
        data_fields = list(insert_info['mappings'].values())
        values = []

        for data_field in data_fields:
            if data_field.startswith('str:'):
                data_field = data_field.replace('str:', '')
                value = f"'{data[data_field]}'"
            elif data_field.startswith('bool:'):
                data_field = data_field.replace('bool:', '')
                value = f"'{data[data_field]}'"
            else:
                value = data[data_field]

            values.append(value)

        return ', '.join(values)

    def get_delete_values(self, delete_info, data):
        keys = list(delete_info['mappings'].keys())
        data_fields = list(delete_info['mappings'].values())
        values = []

        for i, data_field in enumerate(data_fields):
            if data_field.startswith('str:'):
                data_field = data_field.replace('str:', '')
                value = f"{keys[i]} = '{data[data_field]}'"
            else:
                value = f"{keys[i]} = {data[data_field]}"

            values.append(value)

        return ' AND '.join(values)

    def compose_select(self, select_info):
        fields = select_info['fields']
        table = select_info['table']
        where = self.value('where', select_info)

        fields_joined = ', '.join(fields)

        if not where:
            return f"SELECT {fields_joined} FROM {table}"

        return f"SELECT {fields_joined} FROM {table} WHERE {where}"

    def inclusions(self, list_values=None):
        return self.categories(True, list_values)

    def exclusions(self, list_values=None):
        return self.categories(False, list_values)

    def categories(self, inclusion_value, list_values=None):
        if not list_values:
            list_values = self.excl

        particle = ' ' if inclusion_value else ' NOT '

        sql = f"{self.excluded_column}{particle}IN ('"
        sql += "','".join(list_values)
        sql += "')"

        return sql

    def get_query_info(self, queries_info, query_name):
        self.print_query_method(query_name)

        return queries_info[query_name]

    def print_query_method(self, query_name):
        if self.print_query_info_flag:
            print(f"[INFO] Query method: {query_name}")
