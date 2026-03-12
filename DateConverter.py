class DateConverter:
    def format_raw(self, date_input):
        day = date_input[0:2]
        month = date_input[3:5]
        year = date_input[6:10]

        return (year + month + day)

    def format_raw_dmy(self, day, month, year):
        day_str = ("" if day > 9 else "0") + str(day)
        month_str = ("" if month > 9 else "0") + str(month)

        return year + month_str + day_str

    def format_pretty(self, date_input):
        year = date_input[0:4]
        month = date_input[4:6]
        day = date_input[6:8]
        
        return f'{day}/{month}/{year}'