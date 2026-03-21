import datetime


class YearsService:
    def get_values(self):
        year_to = datetime.datetime.today().year
        year_from = year_to - 5

        return [ str(i) for i in range(year_from, year_to + 1) ]