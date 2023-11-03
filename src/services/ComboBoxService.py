import datetime

class ComboBoxService:
    def get_days(self):
        return [ str(i + 1) for i in range(31) ]

    def get_months(self):
        return [ "Enero",  "Febrero",  "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre" ]

    def get_years(self):
        year_to = datetime.datetime.today().year
        year_from = year_to - 5

        return [ str(i) for i in range(year_from, year_to + 1) ]

    def get_categories(self):
        #TODO Get categories from the database service
        categories = [ "Nómina", "Alquiler", "Comida", "Salir", "Ropa", "Otro", "Teléfono", "Agua", "Luz", "Netflix", "Viaje", "Gasolina", "Gimnasio", "Efectivo", "Casa", "Bizum", "Coche", "Transporte", "Cuenta ahorro", "Amazon", "Seguros", "Renta" ]
        return sorted(categories)
