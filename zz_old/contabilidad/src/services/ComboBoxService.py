class ComboBoxService:
    def get_days(self):
        return [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31' ]

    def get_months(self):
        return [ "Enero",  "Febrero",  "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre" ]

    def get_years(self):
        return [ "2019", "2020", "2021" ]

    def get_file_types(self):
        return [ 'csv' ]
