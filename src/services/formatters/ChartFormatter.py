from DateConverter import DateConverter

class ChartFormatter:
    def format_categories(self, categories):
        dict_categories = {}

        for category in categories:
            category_name = category[0]

            if category_name != 'Nómina':
                dict_categories[category_name] = round(abs(category[1]), 2)

        return dict_categories
