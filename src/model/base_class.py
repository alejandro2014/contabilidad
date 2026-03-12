class ModelBaseClass:
    def __init__(self, class_name):
        self.class_name = class_name

    def __str__(self):
        string = f'<{self.class_name}>\n'

        for k in self.__dict__.keys():
            string += f'    {k} = {getattr(self, k)}\n'

        string += f'</{self.class_name}>'

        return string