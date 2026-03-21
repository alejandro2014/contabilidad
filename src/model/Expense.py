from src.model.base_class import ModelBaseClass


class Expense(ModelBaseClass):
    def __init__(self, 
                 file=None, 
                 date=None, 
                 category1=None, category2=None, tag1=None, tag2=None, concept=None, amount=None, file_hash=None, total_amount=None):
        super().__init__('Expense')

        self.file = file
        self.date = date
        self.category1 = category1
        self.category2 = category2
        self.tag1 = tag1
        self.tag2 = tag2
        self.concept = concept
        self.amount = amount
        self.file_hash = file_hash
        self.total_amount = total_amount