from DateConverter import DateConverter

class ChartFormatter:
    def format_categories(self, categories):
        dict_categories = {}

        for category in categories:
            category_name = category[0]

            if category_name != 'Nómina':
                dict_categories[category_name] = round(abs(category[1]), 2)

        return dict_categories
    
    def format_bar_values(self, values):
        months = []
        amounts = []

        for value in values:
            months.append(value[0])
            amounts.append(round(abs(value[1]), 2))

        return {
            'months': months,
            'amounts': amounts
        }

        return [{
            'month': value[0],
            'value': round(abs(value[1]), 2)
        } for value in values ]
