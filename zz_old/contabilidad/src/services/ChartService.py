import time

from src.dao.ChartSqlGenerator import ChartSqlGenerator

from src.misc.DatesGetter import DatesGetter

from src.services.BaseService import BaseService
from src.services.formatters.ChartFormatter import ChartFormatter

class ChartService(BaseService):
    def __init__(self):
        super().__init__()
        self.formatter = ChartFormatter()

        self.sql_generator = ChartSqlGenerator(self.excl_categories)

    def get_pie_chart_info(self, filter):
        if not filter['date']['from'] or not filter['date']['to']:
            return None

        dates = {
            'date_from': filter['date']['from'],
            'date_to': filter['date']['to']
        }

        sql = self.sql_generator.select_pie_chart_categories(dates)

        categories = self.db.select(sql)

        incomes_categories = self.sql_generator.excl_categories['incomes']

        return self.formatter.format_categories(categories, incomes_categories)

    def get_savings_chart_info(self, filter):
        return self.get_chart_info('savings', filter)

    def get_incomes_chart_info(self, filter):
        return self.get_chart_info('incomes', filter)

    def get_chart_info(self, operation, filter):
        dates_getter = DatesGetter()
        dates = dates_getter.get_all_dates(filter)

        sql = getattr(self.sql_generator, f'select_{operation}_by_month')()
        data = self.db.select(sql)
        service_values = getattr(self.formatter, f'format_{operation}_data')(data)

        months = []
        values = []

        for date in dates:
            month = f"0{str(date['month'])}" if date['month'] < 10 else str(date['month'])
            year = str(date['year'])

            month_string = self.month_string_format(month, year)
            months.append(month_string)

            month_exists = year in service_values and month in service_values[year]
            value = service_values[year][month] if month_exists else 0.0
            values.append(value)

        return {
            'months': months,
            'values': values
        }

    def month_string_format(self, month, year):
        return {
            '01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr',
            '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Ago',
            '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'
        }[month] + year
