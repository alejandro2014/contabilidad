from src.misc.DateConverter import DateConverter

class ChartFormatter:
    def format_categories(self, categories, incomes_categories):
        dict_categories = {}

        for category in categories:
            category_name = category[0]

            if category_name not in incomes_categories:
                dict_categories[category_name] = round(abs(category[1]), 2)

        return dict_categories

    def format_savings_data(self, savings_data):
        data_months = {}

        for data in savings_data:
            year = data[0]
            month = data[1]
            quantity = round(data[2], 2)

            if not year in data_months:
                data_months[year] = {}

            if not month in data_months[year]:
                data_months[year][month] = None

            data_months[year][month] = quantity

        return data_months

    def format_incomes_data(self, incomes_data):
        data_months = {}

        for data in incomes_data:
            year = data[0]
            month = data[1]
            quantity = round(data[2], 2)

            if not year in data_months:
                data_months[year] = {}

            if not month in data_months[year]:
                data_months[year][month] = None

            data_months[year][month] = quantity

        return data_months
