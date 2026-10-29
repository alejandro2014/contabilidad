import calendar
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

    def parse(self, date_input):
        return datetime.datetime.strptime(date_input, '%Y%m%d').date()

    def month_dates(self, year_month):
        # First and last day of a month (YYYYMM)
        year, month = int(year_month[0:4]), int(year_month[4:6])

        return f'{year_month}01', f'{year_month}{calendar.monthrange(year, month)[1]:02d}'

    def shift_months(self, date, months, month_end=False):
        # The day is kept when the month has it, otherwise it is the last one (31 March - 1 month = 28 February)
        month_index = date.year * 12 + date.month - 1 + months
        year, month = month_index // 12, month_index % 12 + 1
        last_day = calendar.monthrange(year, month)[1]

        return datetime.date(year, month, last_day if month_end else min(date.day, last_day))

    def is_month_end(self, date):
        return date.day == calendar.monthrange(date.year, date.month)[1]

    def comparison_dates(self, date_from, date_to, mode):
        # Dates (YYYYMMDD) of the period that a range is compared with: the previous one, of the same length, or the
        # same one a year before
        start, end = self.parse(date_from), self.parse(date_to)

        if mode == 'last_year':
            months = -12
        elif start.day == 1:
            # Ranges of whole months (or of this month until today) are compared with the same months before them
            months = -((end.year - start.year) * 12 + end.month - start.month + 1)
        else:
            days = (end - start).days + 1
            previous_end = start - datetime.timedelta(days=1)

            return (previous_end - datetime.timedelta(days=days - 1)).strftime('%Y%m%d'), previous_end.strftime('%Y%m%d')

        previous_start = self.shift_months(start, months)
        previous_end = self.shift_months(end, months, self.is_month_end(end))

        return previous_start.strftime('%Y%m%d'), previous_end.strftime('%Y%m%d')
