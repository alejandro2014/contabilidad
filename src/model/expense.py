class Expense:
    def __init__(self,
                 date=None,
                 category_src = None,
                 subcategory_src = None,
                 title = None,
                 amount = 0,
                 category = None,
                 subcategory = None,
                 category_suggested = None,
                 subcategory_suggested = None):
        self.date = date
        self.category_src = category_src
        self.subcategory_src = subcategory_src
        self.title = title
        self.amount = amount
        self.category = category
        self.subcategory = subcategory
        self.category_suggested = category_suggested
        self.subcategory_suggested = subcategory_suggested
