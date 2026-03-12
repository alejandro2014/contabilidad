class Category:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return f'Category (\n\tname = {self.name},\n\tdescription = {self.description}\n)'
