class CashflowFormatter:
    MONTHS = range(1, 13)

    def format_cashflow(self, values):
        incomes = {}
        expenses = {}

        for is_income, category, month, amount in values:
            # Expenses are negative amounts, but they are shown as the money spent
            if is_income:
                incomes[(category, month)] = amount
            else:
                expenses[(category, month)] = -amount

        incomes_section = self.format_section(incomes, 'Total ingresos')
        expenses_section = self.format_section(expenses, 'Total gastos')

        return {
            'incomes': incomes_section,
            'expenses': expenses_section,
            'balance': self.balance_row(incomes_section['total'], expenses_section['total'])
        }

    def format_section(self, sums, total_title):
        categories = sorted(set([ category for category, month in sums.keys() ]))

        # One row per category: category | January ... December | total
        rows = []

        for category in categories:
            amounts = [ self.round_or_none(sums.get((category, month))) for month in self.MONTHS ]
            rows.append([ category ] + amounts + [ self.sum_amounts(amounts) ])

        return {
            'rows': rows,
            'total': self.total_row(rows, total_title)
        }

    def total_row(self, rows, title):
        # Columns 1 to 13 are the months and the total of each category
        totals = [ self.sum_amounts([ row[column] for row in rows ]) for column in range(1, 14) ]

        return [ title ] + totals

    def balance_row(self, incomes_total, expenses_total):
        balance = []

        for income, expense in zip(incomes_total[1:], expenses_total[1:]):
            if income is None and expense is None:
                balance.append(None)
            else:
                balance.append(round((income or 0.0) - (expense or 0.0), 2))

        return [ 'Balance' ] + balance

    def sum_amounts(self, amounts):
        present = [ amount for amount in amounts if amount is not None ]

        if len(present) == 0:
            return None

        return round(sum(present), 2)

    def round_or_none(self, amount):
        return None if amount is None else round(amount, 2)
