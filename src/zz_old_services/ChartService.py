from src.services.BaseService import BaseService
from src.services.formatters.ChartFormatter import ChartFormatter

class ChartService(BaseService):
    def __init__(self):
        super().__init__()
        self.formatter = ChartFormatter()

    def get_chart_info(self, chart_type, filter=None):
        if chart_type == 'pie':
            return self.get_pie_chart_info(filter)
        
        if chart_type == 'bar':
            return self.get_bar_chart_info()

    def get_pie_chart_info(self, filter):
        dates = {
            'date_from': filter['date']['from'],
            'date_to': filter['date']['to']
        }

        if not dates['date_from'] or not dates['date_to']:
            return None

        sql = self.sql_generator.select_pie_chart_categories(dates)

        categories = self.db.select(sql)

        return self.formatter.format_categories(categories)
    
    def get_bar_chart_info(self):
        sql = self.sql_generator.select_bar_chart_values()

        values = self.db.select(sql)

        return self.formatter.format_bar_values(values)

    def month_name(self, month_number):
        return [ 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre' ][month_number]
