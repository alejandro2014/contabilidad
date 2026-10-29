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
                 balance = None,
                 note = None,
                 tags = None):
        super().__init__(self.__class__.__name__)

        self.id = id
        self.date = date
        self.category_src = category_src
        self.subcategory_src = subcategory_src
        self.title = title
        self.amount = amount
        self.category = category
        # Balance of the account after the movement, when the statement has it
        self.balance = balance
        self.note = note
        self.tags = [] if tags is None else tags

    def __eq__(self, other):
        if type(self) != type(other):
            raise TypeError
        
        return self.date == other.date and \
                self.title == other.title and \
                self.amount == other.amount