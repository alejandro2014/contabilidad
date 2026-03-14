from src.model.base_class import ModelBaseClass


class Rule(ModelBaseClass):
    def __init__(self, category=None, rule=None):
        self.category = category
        self.rule = rule