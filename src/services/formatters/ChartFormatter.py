import re

from DateConverter import DateConverter

class ChartFormatter:
    # Text the bank puts before the shop or the person in the concept of the movements
    TITLE_PREFIXES = [ 'pago en ', 'devolución tarjeta ', 'comisión cajero ', 'reintegro efectivo tarjeta ', 'recibo ',
                       'bizum enviado a ', 'bizum recibido de ', 'transferencia emitida a ', 'transferencia recibida de ',
                       'abono por campaña ', 'www.', 'paypal *' ]
    # Words that don't tell a shop from another, like "EL CORTE INGLES" or "CC LA VAGUADA"
    MERCHANT_STOPWORDS = [ 'el', 'la', 'los', 'las', 'cc' ]

    def format_categories(self, categories):
        dict_categories = {}

        for category in categories:
            category_name = category[0]
            # Expenses are negative amounts, so refunds and money received are subtracted
            amount = round(-category[1], 2)

            # A category with more refunds than expenses cannot be a slice of the pie
            if amount > 0:
                dict_categories[category_name] = amount

        return dict_categories
    
    def format_merchants(self, titles):
        merchants = {}

        # The same shop has a different concept in each branch, and its refunds must be subtracted from it
        for title, amount in titles:
            name = self.merchant_name(title)
            merchants[name] = merchants.get(name, 0.0) - amount

        merchants = { name: round(amount, 2) for name, amount in merchants.items() if round(amount, 2) > 0 }

        return dict(sorted(merchants.items(), key=lambda item: item[1], reverse=True))

    def merchant_name(self, title):
        text = title.strip()

        # Several prefixes can come together, like "Devolución Tarjeta PAYPAL *CORTEFIEL"
        stripped = True
        while stripped:
            stripped = False
            for prefix in self.TITLE_PREFIXES:
                if text.lower().startswith(prefix):
                    text = text[len(prefix):].lstrip()
                    stripped = True

        # The first word is the name of the chain, the rest is the branch and the town: "MERCADONA C ALFREDO MARQUMADRID ES"
        words = [ word for word in re.findall(r'[^\W\d_]+', text) if word.lower() not in self.MERCHANT_STOPWORDS ]

        if len(words) == 0:
            return title.strip()

        return words[0].capitalize()

    def format_income_expense_values(self, expenses, incomes, year_months):
        # Every month of the range has a bar, even without movements, so both series are aligned
        expenses_by_month = dict(expenses)
        incomes_by_month = dict(incomes)
        show_year = self.several_years(year_months)

        return {
            'months': [ self.month_label(year_month, show_year) for year_month in year_months ],
            'short_months': [ self.short_month_label(year_month, show_year) for year_month in year_months ],
            'amounts': [ round(-expenses_by_month.get(year_month, 0.0), 2) for year_month in year_months ],
            'incomes': [ round(incomes_by_month.get(year_month, 0.0), 2) for year_month in year_months ]
        }

    def format_category_evolution(self, values, categories, year_months):
        sums = { (category, year_month): amount for category, year_month, amount in values }
        show_year = self.several_years(year_months)

        return {
            'months': [ self.month_label(year_month, show_year) for year_month in year_months ],
            'short_months': [ self.short_month_label(year_month, show_year) for year_month in year_months ],
            'series': {
                category: [ round(-sums.get((category, year_month), 0.0), 2) for year_month in year_months ]
                for category in categories
            }
        }

    def format_top_expenses(self, expenses):
        return [ {
            'date': self.dates_range_label(date_from, date_to),
            'title': title,
            'category': category,
            'amount': round(-amount, 2),
            'count': count
        } for date_from, date_to, title, category, amount, count in expenses ]

    def dates_range_label(self, date_from, date_to):
        if date_from == date_to:
            return DateConverter().format_pretty(date_from)

        return f'{DateConverter().format_pretty(date_from)} - {DateConverter().format_pretty(date_to)}'

    def group_categories(self, categories, max_slices, others_name='Otros'):
        # More slices than colors can't be told apart, so the smallest categories are added up
        if len(categories) <= max_slices:
            return dict(categories)

        names = list(categories.keys())
        grouped = { name: categories[name] for name in names[:max_slices - 1] }
        grouped[others_name] = round(sum([ categories[name] for name in names[max_slices - 1:] ]), 2)

        return grouped

    def format_kpis(self, categories, bar_info, pending_count):
        expenses = round(sum(bar_info['amounts']), 2)
        incomes = round(sum(bar_info['incomes']), 2)
        balance = round(incomes - expenses, 2)
        months_no = len(bar_info['amounts'])

        top_category = None
        if len(categories) > 0:
            name = max(categories, key=categories.get)
            top_category = { 'name': name, 'amount': categories[name] }

        max_month = None
        if months_no > 0 and max(bar_info['amounts']) > 0:
            index = bar_info['amounts'].index(max(bar_info['amounts']))
            max_month = { 'name': bar_info['months'][index], 'amount': bar_info['amounts'][index] }

        return {
            'expenses': expenses,
            'incomes': incomes,
            'balance': balance,
            # Without incomes the savings rate has no meaning
            'savings_rate': round(balance / incomes * 100.0, 1) if incomes > 0 else None,
            'monthly_average': round(expenses / months_no, 2) if months_no > 0 else 0.0,
            'top_category': top_category,
            'max_month': max_month,
            'pending': pending_count
        }

    def year_months(self, date_from, date_to):
        year, month = int(date_from[0:4]), int(date_from[4:6])
        year_to, month_to = int(date_to[0:4]), int(date_to[4:6])
        year_months = []

        while (year, month) <= (year_to, month_to):
            year_months.append(f'{year}{month:02d}')
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)

        return year_months

    def several_years(self, year_months):
        return len(set([ year_month[0:4] for year_month in year_months ])) > 1

    def month_label(self, year_month, show_year):
        year = year_month[0:4]
        month_number = int(year_month[4:6])

        name = self.month_name(month_number - 1)

        return f'{name} {year}' if show_year else name

    def short_month_label(self, year_month, show_year):
        # Labels of the chart axes, which don't have room for the full name
        name = self.month_name(int(year_month[4:6]) - 1)[0:3]

        return f'{name} {year_month[2:4]}' if show_year else name

    def month_name(self, month_number):
        return [ 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre' ][month_number]
