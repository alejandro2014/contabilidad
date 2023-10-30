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
        return [ {
            'id': expense[0],
            'date': expense[1],
            'concept': expense[2],
            'quantity': str(expense[3])
        } for expense in expenses ]
