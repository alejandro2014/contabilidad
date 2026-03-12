from PySide2.QtWidgets import QCheckBox, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QMessageBox

from src.dialogs.BaseDialog import BaseDialog

from src.services.ExpenseTypesService import ExpenseTypesService

from src.widgets.BaseWidget import BaseWidget

from globals import widgets_pool as wpool

class AddCategoryDialog(BaseDialog):
    def __init__(self, parent):
        self.parent = parent
        self.id = 'add-category-dialog'

        super(AddCategoryDialog, self).__init__(self.parent, self.id)

        self.expense_types_service = ExpenseTypesService()

        self.name_label, self.name_textbox = self.create_line_edit("Nombre:")
        self.description_label, self.description_textbox = self.create_line_edit("Descripción:")
        self.button_box = self.create_button_box(self.id)

        self.checkbox_savings = QCheckBox("Ahorro")
        self.checkbox_incomes = QCheckBox("Ingreso")

        self.create_layout()
        self.show()

    def create_layout(self):
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_textbox)

        description_layout = QHBoxLayout()
        description_layout.addWidget(self.description_label)
        description_layout.addWidget(self.description_textbox)

        checkboxes_panel = QHBoxLayout()
        checkboxes_panel.addWidget(self.checkbox_savings)
        checkboxes_panel.addWidget(self.checkbox_incomes)

        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(name_layout)
        dialog_layout.addLayout(description_layout)
        dialog_layout.addLayout(checkboxes_panel)
        dialog_layout.addLayout(self.button_box)

        self.setLayout(dialog_layout)

    def save_category(self):
        category_name = self.name_textbox.text()
        category_description = self.description_textbox.text()

        is_savings = self.checkbox_savings.isChecked()
        is_income = self.checkbox_incomes.isChecked()

        if self.save_category_name_error(category_name):
            return

        self.expense_types_service.add_category(category_name, category_description, is_savings, is_income)
        self.accept()

        wpool.execute('classifier', 'refresh')
        wpool.execute('configure-expenses-dialog', 'refresh')
        wpool.execute('menubar', 'refresh')

    def save_category_name_error(self, category_name):
        if category_name == '':
            QMessageBox.warning(self, "Nombre vacío", "El nombre de la categoría no puede estar vacío")
            return True

        category_exists = self.expense_types_service.check_category_exists(category_name)

        if category_exists:
            QMessageBox.warning(self, "La categoría ya existe", f'Ya se ha introducido una categoría "{category_name}"')
            return True

        return False
