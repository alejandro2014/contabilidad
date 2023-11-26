from PySide2.QtWidgets import QWidget, QStatusBar

from src.events.ListenerNode import ListenerNode
from src.services.expenses_service import ExpensesService

class StatusBar(QStatusBar, ListenerNode):
    def __init__(self, listeners_pool, *args, **kwargs):
        super(StatusBar, self).__init__(*args, **kwargs)
        ListenerNode.__init__(self, 'status-bar', listeners_pool)

        self.expenses_service = ExpensesService()

        self.refresh()

    def refresh(self):
        pending = self.expenses_service.get_pending_expenses_count()
        classified = self.expenses_service.get_classified_expenses_count()

        self.showMessage(f'Pendientes: {str(pending)}, Clasificados: {str(classified)}', 0)