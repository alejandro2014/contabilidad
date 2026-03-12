import datetime

from src.services.ExpenseTypesService import ExpenseTypesService

class ComboBoxService:
    def __init__(self):
        self.expense_types_service = ExpenseTypesService()

    def get_days(self):
        return [ str(i + 1) for i in range(31) ]

    def get_months(self):
        return [ "Enero",  "Febrero",  "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre" ]

    def get_years(self):
        year_to = datetime.datetime.today().year
        year_from = year_to - 5

        return [ str(i) for i in range(year_from, year_to + 1) ]

    def get_categories(self):
        return self.expense_types_service.get_categories_simple()
