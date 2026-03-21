from globals import widgets_pool

from PySide2.QtWidgets import QWidget

from globals import widgets_pool as wpool

class RootWidget(QWidget):
    def __init__(self):
        super(RootWidget, self).__init__()

    def get_widgets_from_pool(self):
        if not hasattr(self, 'widget_ids') or len(self.widget_ids) == 0:
            return

        for widget_id in self.widget_ids:
            attr_name = widget_id.replace('-', '_')
            widget = wpool.get(widget_id)
            setattr(self, attr_name, widget)

    def init_widgets(self):
        pass
