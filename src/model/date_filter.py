from src.model.base_class import ModelBaseClass

class DateFilter(ModelBaseClass):
    def __init__(self,
                year_from = None,
                month_from = None,
                day_from = None,
                year_to = None,
                month_to = None,
                day_to = None):
        super().__init__(self.__class__.__name__)

        self.year_from = year_from
        self.month_from = month_from
        self.day_from = day_from
        self.year_to = year_to
        self.month_to = month_to
        self.day_to = day_to