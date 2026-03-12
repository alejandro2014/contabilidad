class DatesGetter:
    def get_all_dates(self, filter):
        year_from, year_to, month_from, month_to = self.get_dates_from_filter(filter)

        if year_from == year_to:
            return self.get_dates_same_year(year_from, month_from, month_to)

        if year_from < year_to:
            return self.get_dates_different_years(year_from, year_to, month_from, month_to)

        print('Error: El año final no puede ser anterior al inicial')
        return []

    def get_dates_same_year(self, year, month_from, month_to):
        dates = []

        for month in range(month_from, month_to + 1):
            dates.append(self.new_date(year, month))

        return dates

    def get_dates_different_years(self, year_from, year_to, month_from, month_to):
        dates = []
        complete_years = year_to - year_from - 1

        for month in range(month_from, 13):
            dates.append(self.new_date(year_from, month))

        for year in range(year_from + 1, year_from + complete_years + 1):
            for month in range(1, 13):
                dates.append(self.new_date(year, month))

        for month in range(1, month_to + 1):
            dates.append(self.new_date(year_to, month))

        return dates

    def new_date(self, year, month):
        return {
            'month': month,
            'year': year
        }

    def get_dates_from_filter(self, filter):
        date_from = filter['date']['from'][:6]
        date_to = filter['date']['to'][:6]

        year_from = int(date_from[:4])
        year_to = int(date_to[:4])
        month_from = int(date_from[4:])
        month_to = int(date_to[4:])

        return year_from, year_to, month_from, month_to
