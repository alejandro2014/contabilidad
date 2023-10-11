class ComboBoxService:
    def get_days(self):
        return [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31' ]

    def get_months(self):
        return [ "Enero",  "Febrero",  "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre" ]

    def get_years(self):
        return [ "2019", "2020", "2021", "2022", "2023" ]

    def get_categories(self):
        #TODO Get categories from the database service
        categories = [ "Nómina", "Alquiler", "Comida", "Salir", "Ropa", "Otro", "Teléfono", "Agua", "Luz", "Netflix", "Viaje", "Gasolina", "Gimnasio", "Efectivo", "Casa", "Bizum", "Coche", "Transporte", "Cuenta ahorro", "Amazon" ]
        return sorted(categories)
