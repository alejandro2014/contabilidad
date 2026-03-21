import sys
from PySide6 import QtCore, QtWidgets

from dialogs.ConfigureExpensesDialog import ConfigureExpensesDialog
from dialogs.LoadFileDialog import LoadFileDialog

from services.ExpensesService import ExpensesService
from services.ExpenseTypesService import ExpenseTypesService
from services.UseCasesService import UseCasesService

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()1

        self.__use_cases_service = UseCasesService()
        self.__expense_types_service = ExpenseTypesService()
        self.__expenses_service = ExpensesService()

        self.setWindowTitle('Contabilidad')
        self.resize(1024, 768)

        self.menubar = self.menuBar()
        self.load_options_menu()
        self.set_status_bar()

        self.table = QtWidgets.QTableWidget(1, 4)
        self.columnLabels = [ "Fecha", "Concepto", "Tipo", "Cantidad" ]
        self.table.setHorizontalHeaderLabels(self.columnLabels)

        expenses = self.__expenses_service.get_all_expenses()

        categories = [ 'date', 'concept', 'type', 'quantity' ]

        for index_row, expense in enumerate(expenses):
            self.table.insertRow(index_row)

            for index_category, category in enumerate(categories):
                self.table.setItem(index_row, index_category, QtWidgets.QTableWidgetItem(expense[category]))

        self.table.resizeColumnsToContents()

        #button_box = QtWidgets.QHBoxLayout()
        #button_box.addWidget(button_ok)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table)

        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(self.layout)
        #self.layout.addLayout(button_box)

        #self.setLayout(self.layout)
        #self.show()

    def load_options_menu(self):
        menu_gastos = self.menubar.addMenu('Gastos')

        load_expenses_file_action = menu_gastos.addAction('Cargar fichero')
        load_expenses_file_action.triggered.connect(self.load_expenses_file)

        classify_expenses_action = menu_gastos.addAction('Modificar')
        classify_expenses_action.triggered.connect(self.classify_expenses)

        print_report_action = menu_gastos.addAction('Imprimir informe')
        print_report_action.triggered.connect(self.print_report)

        menu_gastos.addSeparator()

        exit_app_action = menu_gastos.addAction('Salir')
        exit_app_action.triggered.connect(self.exit_app)

        menu_gastos = self.menubar.addMenu('Ver')

        view_expenses_table_action = menu_gastos.addAction('Ver tabla')
        view_expenses_table_action.triggered.connect(self.view_expenses_table)

        view_expenses_charts_action = menu_gastos.addAction('Ver graficos')
        view_expenses_charts_action.triggered.connect(self.view_expenses_charts)

        menu_configuracion = self.menubar.addMenu('Configuracion')

        configure_columns_action = menu_configuracion.addAction('Columnas de entrada')
        configure_columns_action.triggered.connect(self.configure_columns)

        configure_expense_types_action = menu_configuracion.addAction('Tipos de gastos')
        configure_expense_types_action.triggered.connect(self.configure_expense_types)

    def load_expenses_file(self):
        load_file_dialog = LoadFileDialog(self)

    def classify_expenses(self):
        print('Modificar')

    def print_report(self):
        print('Imprimir informe')

    def exit_app(self):
        QtCore.QCoreApplication.instance().quit()

    def view_expenses_table(self):
        print('Ver tabla')

    def view_expenses_charts(self):
        print('Ver graficos')

    def configure_columns(self):
        print('Columnas de entrada')

    def configure_expense_types(self):
        configure_expenses_dialog = ConfigureExpensesDialog(self)

    def set_status_bar(self):
        status_bar = self.statusBar()
        status_bar.showMessage('1245 registros, desde 09/2019 hasta 11/2020')

    def get_use_cases_service(self):
        return self.__use_cases_service

    def get_expenses_service(self):
        return self.__expenses_service

    def get_expense_types_service(self):
        return self.__expense_types_service
