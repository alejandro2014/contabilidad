from src.dao.ChartSqlGenerator import ChartSqlGenerator

from src.services.BaseService import BaseService
from src.services.formatters.ChartFormatter import ChartFormatter

class ChartService(BaseService):
    def __init__(self):
        super().__init__()
        self.formatter = ChartFormatter()
        self.sql_generator = ChartSqlGenerator()

    def get_pie_chart_info(self, filter):
        dates = {
            'date_from': filter['date']['from'],
            'date_to': filter['date']['to']
        }

        if not dates['date_from'] or not dates['date_to']:
            return {}

        sql = self.sql_generator.select_pie_chart_categories(dates)

        categories = self.db.select(sql)

        return self.formatter.format_categories(categories)

    def month_name(self, month_number):
        return [ 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre' ][month_number]
