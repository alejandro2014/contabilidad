from DateConverter import DateConverter

class PendingExpensesFormatter:
    def csv_to_expense(self, csv_line, formatter):
        fields = formatter['fields']

        return {
            'date': DateConverter().format_raw(csv_line['field_' + str(fields['date'])]),
            'concept': csv_line['field_' + str(fields['concept'])],
            'value': csv_line['field_' + str(fields['value'])].replace(',', '')
        }

    def format_expenses(self, expenses):
        return list(map(lambda expense: {
            'date': expense[0],
            'concept': expense[1],
            'quantity': str(expense[2])
        }, expenses))
