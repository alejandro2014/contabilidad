from DateConverter import DateConverter

from src.services.BaseService import BaseService
from src.services.formatters.ChartFormatter import ChartFormatter

class ChartService(BaseService):
    TOP_EXPENSES_NO = 25
    # Months before the current one that make its average
    AVERAGE_MONTHS_NO = 12

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

    def get_merchants_info(self, filter, category):
        dates = self.get_dates(filter)

        if dates is None:
            return {}

        titles = self.db.select(self.sql_generator.select_category_titles(dates, category))

        return self.formatter.format_merchants(titles)

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

    def expenses_filter(self, filter, year_month=None, category=None, search_value=None):
        # Filter of the table with the movements behind a part of a chart: those of its month (inside the range of
        # the dashboard), its type and its concept
        date_from, date_to = filter['date']['from'], filter['date']['to']

        if year_month is not None:
            month_from, month_to = DateConverter().month_dates(year_month)
            date_from, date_to = max(date_from, month_from), min(date_to, month_to)

        return {
            'date': { 'from': date_from, 'to': date_to },
            'category': category,
            'search_value': search_value
        }

    def get_kpis(self, filter, categories, bar_info, comparison=None):
        dates = self.get_dates(filter)
        pending_count = 0 if dates is None else self.get_single_value(self.sql_generator.select_pending_expenses_count_between(dates))

        kpis = self.formatter.format_kpis(categories, bar_info, pending_count)
        # Compared with the previous period ('previous') or with the same one last year ('last_year')
        kpis['changes'] = None

        if dates is not None and comparison is not None:
            date_from, date_to = DateConverter().comparison_dates(dates['date_from'], dates['date_to'], comparison)
            previous_bar_info = self.get_bar_chart_info({ 'date': { 'from': date_from, 'to': date_to } })
            previous_kpis = self.formatter.format_kpis({}, previous_bar_info, 0)

            kpis['changes'] = self.formatter.format_kpi_changes(kpis, previous_kpis)

        return kpis

    def get_category_average_info(self, filter):
        # The month of the end of the range, compared with the months before it
        dates = self.get_dates(filter)

        if dates is None:
            return None

        year_month = dates['date_to'][0:6]
        date_converter = DateConverter()
        first_month = date_converter.shift_months(date_converter.parse(dates['date_to']), -self.AVERAGE_MONTHS_NO).strftime('%Y%m')
        previous_year_months = self.formatter.year_months(f'{first_month}01', f'{year_month}01')[:-1]

        values = self.db.select(self.sql_generator.select_category_month_values({ 'date_from': f'{first_month}01', 'date_to': dates['date_to'] }))

        return self.formatter.format_category_average(values, year_month, previous_year_months)

    def get_balance_chart_info(self, filter):
        dates = self.get_dates(filter)

        if dates is None:
            return self.formatter.format_balances([], [])

        movements = self.db.select(self.sql_generator.select_balances(dates))
        year_months = self.formatter.year_months(dates['date_from'], dates['date_to'])

        return self.formatter.format_balances(movements, year_months)
