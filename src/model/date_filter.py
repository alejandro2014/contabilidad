class DateFilter:
    def __init__(self,
                year_from = None,
                month_from = None,
                day_from = None,
                year_to = None,
                month_to = None,
                day_to = None):
        self.year_from = year_from
        self.month_from = month_from
        self.day_from = day_from
        self.year_to = year_to
        self.month_to = month_to
        self.day_to = day_to

    def __str__(self):
        return (
            f'<model.DateFilter>'
            f'    year_from = {self.year_from}'
            f'    month_from = {self.month_from}'
            f'    day_from = {self.day_from}'
            f'    year_to = {self.year_to}'
            f'    month_to = {self.month_to}'
            f'    day_to = {self.day_to}'
            f'</model.DateFilter>'
        )