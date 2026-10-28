import datetime

class DateConverter:
    def format_raw_dmy(self, day, month, year):
        day_str = ("" if day > 9 else "0") + str(day)
        month_str = ("" if month > 9 else "0") + str(month)

        return year + month_str + day_str

    def format_pretty(self, date_input):
        year = date_input[0:4]
        month = date_input[4:6]
        day = date_input[6:8]
        
        return f'{day}/{month}/{year}'

    def period_dates(self, period, today):
        # First and last day of one of the quick periods of the date filter
        if period == 'this_month':
            return today.replace(day=1), today

        if period == 'last_month':
            last_day = today.replace(day=1) - datetime.timedelta(days=1)
            return last_day.replace(day=1), last_day

        if period in [ 'last_3_months', 'last_12_months' ]:
            # The current month is one of them
            months_back = 2 if period == 'last_3_months' else 11
            month_index = today.year * 12 + today.month - 1 - months_back
            return datetime.date(month_index // 12, month_index % 12 + 1, 1), today

        if period == 'this_year':
            return datetime.date(today.year, 1, 1), today

        if period == 'last_year':
            return datetime.date(today.year - 1, 1, 1), datetime.date(today.year - 1, 12, 31)
