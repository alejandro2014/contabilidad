class SqlGenerator:
    def insert_expense_not_classified(self, concept_line):
        date_record = concept_line['date']
        concept = concept_line['concept']
        quantity = concept_line['value']

        return "INSERT INTO expenses_not_classified (date_record, concept, quantity) VALUES ('" + date_record + "', '" + concept + "', " + quantity + ")"

    def get_all_expenses(self):
        return "SELECT date_record, concept, quantity, type FROM expenses_not_classified"

    def get_expense_types_full(self):
        return "SELECT category, comment FROM expense_types ORDER BY category"
