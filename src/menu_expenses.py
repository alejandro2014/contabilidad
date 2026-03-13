from PySide6.QtCore import QCoreApplication

#from src.dialogs.LoadFileDialog import LoadFileDialog
#from src.screens.ClassifyExpensesScreen import ClassifyExpensesScreen

class MenuExpenses:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menubar = self.main_window.menuBar()

        menu_gastos = self.menubar.addMenu('Gastos')

        load_expenses_file_action = menu_gastos.addAction('Cargar fichero')
        load_expenses_file_action.triggered.connect(self.load_expenses_file)

        classify_expenses_action = menu_gastos.addAction('Clasificar pendientes')
        classify_expenses_action.triggered.connect(self.classify_expenses)

        print_report_action = menu_gastos.addAction('Imprimir informe')
        print_report_action.triggered.connect(self.print_report)

        menu_gastos.addSeparator()

        exit_app_action = menu_gastos.addAction('Salir')
        exit_app_action.triggered.connect(self.exit_app)

    def load_expenses_file(self):
        LoadFileDialog(self, self.listeners_pool)

    def classify_expenses(self):
        classify_expenses_screen = ClassifyExpensesScreen(self.listeners_pool)
        self.setCentralWidget(classify_expenses_screen)

    def print_report(self):
        return
    
    def exit_app(self):
        QCoreApplication.instance().quit()
