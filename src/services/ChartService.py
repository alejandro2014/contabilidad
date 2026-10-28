from src.services.BaseService import BaseService
from src.services.formatters.ChartFormatter import ChartFormatter

class ChartService(BaseService):
    TOP_EXPENSES_NO = 25

    def __init__(self):
        super().__init__()
        self.formatter = ChartFormatter()

    def get_chart_info(self, chart_type, filter=None):
        if chart_type == 'pie':
            return self.get_pie_chart_info(filter)

        if chart_type == 'bar':
            return self.get_bar_chart_info(filter)

        if chart_type == 'top':
            return self.get_top_expenses(filter)

    def get_dates(self, filter):
        dates = {
            'date_from': filter['date']['from'],
            'date_to': filter['date']['to']
        }

        if not dates['date_from'] or not dates['date_to']:
            return None

        return dates

    def get_pie_chart_info(self, filter):
        dates = self.get_dates(filter)

        if dates is None:
            return {}

        sql = self.sql_generator.select_pie_chart_categories(dates)

        categories = self.db.select(sql)

        return self.formatter.format_categories(categories)

    def get_bar_chart_info(self, filter):
        dates = self.get_dates(filter)

        if dates is None:
            return self.formatter.format_income_expense_values([], [], [])

        expenses = self.db.select(self.sql_generator.select_bar_chart_values(dates))
        incomes = self.db.select(self.sql_generator.select_income_chart_values(dates))
        year_months = self.formatter.year_months(dates['date_from'], dates['date_to'])

        return self.formatter.format_income_expense_values(expenses, incomes, year_months)

    def get_evolution_chart_info(self, filter, categories=[]):
        dates = self.get_dates(filter)

        if dates is None:
            return self.formatter.format_category_evolution([], [], [])

        values = self.db.select(self.sql_generator.select_category_month_values(dates))
        year_months = self.formatter.year_months(dates['date_from'], dates['date_to'])

        return self.formatter.format_category_evolution(values, categories, year_months)

    def get_top_expenses(self, filter):
        dates = self.get_dates(filter)

        if dates is None:
            return []

        expenses = self.db.select(self.sql_generator.select_top_expenses(dates, self.TOP_EXPENSES_NO))

        return self.formatter.format_top_expenses(expenses)

    def get_kpis(self, filter, categories, bar_info):
        dates = self.get_dates(filter)
        pending_count = 0 if dates is None else self.get_single_value(self.sql_generator.select_pending_expenses_count_between(dates))

        return self.formatter.format_kpis(categories, bar_info, pending_count)
