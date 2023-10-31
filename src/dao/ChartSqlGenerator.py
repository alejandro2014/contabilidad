class ChartSqlGenerator:
    def select_pie_chart_categories(self, params):
        date_from = params['date_from']
        date_to = params['date_to']

        return f"SELECT category, sum(amount) AS amnt FROM expenses WHERE category IS NOT NULL AND date BETWEEN '{date_from}' AND '{date_to}' GROUP BY category ORDER BY abs(amnt) DESC"
