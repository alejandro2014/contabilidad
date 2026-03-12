class Expense:
    def __init__(self, id=None, file=None, date=None, category1=None, category2=None, tag1=None, tag2=None, concept=None, amount=None, hash=None):
        self.id = id
        self.file = file
        self.date = date
        self.category1 = category1
        self.category2 = category2
        self.tag1 = tag1
        self.tag2 = tag2
        self.concept = concept
        self.amount = amount
        self.hash = hash