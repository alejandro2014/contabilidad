from src.model.base_class import ModelBaseClass

class Expense(ModelBaseClass):
    def __init__(self,
                 id = None,
                 date = None,
                 category_src = None,
                 subcategory_src = None,
                 title = None,
                 amount = 0,
                 category = None,
                 subcategory = None,
                 category_suggested = None,
                 subcategory_suggested = None):
        super().__init__(self.__class__.__name__)

        self.id = id
        self.date = date
        self.category_src = category_src
        self.subcategory_src = subcategory_src
        self.title = title
        self.amount = amount
        self.category = category
        self.subcategory = subcategory
        self.category_suggested = category_suggested
        self.subcategory_suggested = subcategory_suggested

    def __eq__(self, other):
        if type(self) != type(other):
            raise TypeError
        
        return self.date == other.date and \
                self.title == other.title and \
                self.amount == other.amount