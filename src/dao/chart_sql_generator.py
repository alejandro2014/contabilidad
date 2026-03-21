from src.config.ConfigLoader import ConfigLoader
from src.dao.base_sql_generator import BaseSqlGenerator

class ChartSqlGenerator(BaseSqlGenerator):
    def __init__(self, excl_categories):
        super(ChartSqlGenerator, self).__init__(excl_categories)
        self.queries_info = ConfigLoader().load_config_file('db/queries-info-chart')

    def select_pie_chart_categories(self, params):
        query_info = self.get_query_info(self.queries_info, 'select_pie_chart_categories')

        query_info['where'] = f"date_record between '{params['date_from']}' and '{params['date_to']}' AND {self.exclusions()} group by type order by abs(qty) desc"

        return self.compose_select(query_info)

    def select_savings_by_month(self):
        query_info = self.get_query_info(self.queries_info, 'select_savings_by_month')

        query_info['where'] = f"{self.inclusions(self.excl_savings)} group by year, month"

        return self.compose_select(query_info)

    def select_incomes_by_month(self):
        query_info = self.get_query_info(self.queries_info, 'select_incomes_by_month')

        query_info['where'] = f"{self.exclusions(self.excl_savings)} AND quantity > 0 group by year, month"

        return self.compose_select(query_info)
