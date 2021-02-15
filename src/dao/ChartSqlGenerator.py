class ChartSqlGenerator:
    def select_pie_chart_categories(self, params):
        date_from = params['date_from']
        date_to = params['date_to']

        return "select type, sum(quantity) as qty from expenses_classified where date_record between '" + date_from + "' and '" + date_to + "' group by type order by abs(qty) desc"
