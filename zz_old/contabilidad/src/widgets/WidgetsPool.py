class WidgetsPool:
    def __init__(self):
        self.widgets = {}
        self.show_info = True

    def init(self):
        widget_ids = self.widgets.keys()

        for widget_id in widget_ids:
            widget = self.widgets[widget_id]
            widget.get_widgets_from_pool()
            widget.create_layout()
            widget.init_widgets()

    def add(self, widget_id, reference):
        if widget_id in self.widgets:
            self.delete(widget_id)

        self.widgets[widget_id] = reference

    def delete(self, widget_id):
        del self.widgets[widget_id]

    def get(self, widget_id):
        return self.widgets[widget_id]

    def execute(self, widget_id, method_name, params=None):
        self.print_info(f'Executing {widget_id}.{method_name}...')

        if widget_id not in self.widgets:
            self.print_info(f'{widget_id} does not exist')
            return None

        widget = self.widgets[widget_id]
        method = getattr(widget, method_name)

        if params is None:
            return method()

        return method(params)

    def print_info(self, message):
        if self.show_info:
            print(f'[INFO] {message}')
