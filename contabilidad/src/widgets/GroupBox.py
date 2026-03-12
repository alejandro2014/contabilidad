from PySide2.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout

# TODO Refactor layour
class GroupBox(QGroupBox):
    def __init__(self, title, elements, layout='vertical'):
        super(GroupBox, self).__init__(title)

        group_box_layout = self.get_layout(layout)

        for element in elements:
            group_box_layout.addWidget(element)

        self.setLayout(group_box_layout)

    def get_layout(self, layout):
        if layout == 'horizontal':
            return QHBoxLayout()

        if layout == 'vertical':
            return QVBoxLayout()

        return None
