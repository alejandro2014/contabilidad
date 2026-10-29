from PySide6 import QtWidgets
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QStyle, QTableWidgetItem, QVBoxLayout

from src.dialogs.ErrorDialog import ErrorDialog
from src.dialogs.WidgetCreator import WidgetCreator

from src.services.ComboBoxService import ComboBoxService
from src.services.RulesService import RulesService

class ConfigureRulesDialog(QDialog):
    RULE_COLUMN = 0
    CATEGORY_COLUMN = 1

    def __init__(self, parent):
        super(ConfigureRulesDialog, self).__init__(parent)

        self.widget_creator = WidgetCreator()
        self.rules_service = RulesService()
        self.categories = ComboBoxService().get_categories()

        # Same order as the table rows, which is the priority of the rules
        self.rules = []

        self.setWindowTitle("Reglas de clasificación")
        self.resize(700, 650)
        self.setModal(True)

        help_label = QLabel("Al cargar un fichero, cada gasto toma el tipo de la primera regla cuyo texto aparece en su concepto")
        help_label.setWordWrap(True)

        self.table = QtWidgets.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels([ "Contiene", "Tipo de gasto" ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.cellChanged.connect(self.rule_text_changed)

        # New rule
        self.new_rule_textbox = QLineEdit()
        self.new_rule_textbox.setPlaceholderText("Texto que contiene el concepto")
        self.new_rule_category = self.widget_creator.create_categories_combobox()
        button_add = self.widget_creator.create_button("Añadir regla", "upload", self.add_rule)

        add_layout = QHBoxLayout()
        add_layout.addWidget(self.new_rule_textbox)
        add_layout.addWidget(self.new_rule_category)
        add_layout.addWidget(button_add)

        # Check which rule a concept would match
        self.test_textbox = QLineEdit()
        self.test_textbox.setPlaceholderText("Escribe un concepto para ver qué regla se aplicaría")
        self.test_textbox.textChanged.connect(self.test_concept)
        self.test_result = QLabel()

        test_layout = QHBoxLayout()
        test_layout.addWidget(QLabel("Probar:"))
        test_layout.addWidget(self.test_textbox)

        button_up = self.widget_creator.create_button("Subir", "upload", lambda: self.move_selected_rule(-1))
        button_down = self.widget_creator.create_button("Bajar", "upload", lambda: self.move_selected_rule(1))

        # There are no arrow images in the configuration folder
        button_up.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        button_down.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
        button_remove = self.widget_creator.create_button("Eliminar seleccionadas", "bin", self.remove_selected_rules)
        button_ok = self.widget_creator.create_button("Aceptar", "ok", self.accept)

        button_box = QHBoxLayout()
        button_box.addWidget(button_up)
        button_box.addWidget(button_down)
        button_box.addWidget(button_remove)
        button_box.addStretch()
        button_box.addWidget(button_ok)

        layout = QVBoxLayout()
        layout.addWidget(help_label)
        layout.addLayout(add_layout)
        layout.addWidget(self.table)
        layout.addLayout(test_layout)
        layout.addWidget(self.test_result)
        layout.addLayout(button_box)
        self.setLayout(layout)

        self.reload()
        self.show()

    def reload(self, selected_row = None):
        self.rules = self.rules_service.get_rules()

        # Avoid cellChanged updating the database while the table is filled
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        for row, rule in enumerate(self.rules):
            self.table.insertRow(row)
            self.table.setItem(row, self.RULE_COLUMN, QTableWidgetItem(rule['rule']))
            self.table.setCellWidget(row, self.CATEGORY_COLUMN, self.create_category_combobox(rule))

        self.table.blockSignals(False)
        self.table.resizeColumnToContents(self.RULE_COLUMN)

        if selected_row is not None and 0 <= selected_row < len(self.rules):
            self.select_row(selected_row)

        self.test_concept()

    def create_category_combobox(self, rule):
        combo = QComboBox()
        combo.addItems(self.categories)

        # Keep the category of the rule even if the expense type has been removed
        if rule['category'] not in self.categories:
            combo.addItem(rule['category'])

        combo.setCurrentText(rule['category'])
        combo.currentTextChanged.connect(lambda category: self.rule_category_changed(rule, category))

        return combo

    def rule_category_changed(self, rule, category):
        self.rules_service.update_rule(rule['priority'], rule['rule'], category)
        rule['category'] = category

        self.test_concept()

    def rule_text_changed(self, row, column):
        if column != self.RULE_COLUMN:
            return

        rule = self.rules[row]
        new_text = self.table.item(row, column).text().strip()

        if new_text == '':
            ErrorDialog(self, title = "Error: Regla vacía", message = "El texto de la regla no puede estar vacío")
            self.reload(row)
            return

        if new_text != rule['rule'] and self.rules_service.rule_exists(rule['category'], new_text):
            ErrorDialog(self, title = "Error: La regla ya existe", message = f'Ya hay una regla "{new_text}" para "{rule["category"]}"')
            self.reload(row)
            return

        self.rules_service.update_rule(rule['priority'], new_text, rule['category'])
        rule['rule'] = new_text

        self.test_concept()

    def add_rule(self):
        rule = self.new_rule_textbox.text().strip()
        category = self.new_rule_category.currentText()

        if rule == '':
            ErrorDialog(self, title = "Error: Regla vacía", message = "El texto de la regla no puede estar vacío")
            return

        if self.rules_service.rule_exists(category, rule):
            ErrorDialog(self, title = "Error: La regla ya existe", message = f'Ya hay una regla "{rule}" para "{category}"')
            return

        self.rules_service.add_rule(category, rule)
        self.new_rule_textbox.clear()

        # New rules have the lowest priority, at the end of the list
        self.reload(len(self.rules))

    def remove_selected_rules(self):
        rows = self.get_selected_rows()

        if len(rows) == 0 or not self.confirm_remove_rules(rows):
            return

        for row in rows:
            self.rules_service.delete_rule_by_priority(self.rules[row]['priority'])

        self.reload()

    def confirm_remove_rules(self, rows):
        if len(rows) == 1:
            rule = self.rules[rows[0]]
            message = f'¿Eliminar la regla "{rule["rule"]}" → {rule["category"]}?'
        else:
            message = f'¿Eliminar las {len(rows)} reglas seleccionadas?'

        answer = QMessageBox.question(self, "Eliminar reglas", message)

        return answer == QMessageBox.StandardButton.Yes

    def move_selected_rule(self, offset):
        rows = self.get_selected_rows()

        if len(rows) != 1:
            return

        row = rows[0]
        new_row = row + offset

        if new_row < 0 or new_row >= len(self.rules):
            return

        self.rules_service.swap_priorities(self.rules[row]['priority'], self.rules[new_row]['priority'])
        self.reload(new_row)

    def test_concept(self, concept = None):
        concept = self.test_textbox.text()

        if concept.strip() == '':
            self.test_result.setText('')
            return

        index = self.rules_service.find_rule_index(self.rules, concept)

        if index is None:
            self.test_result.setText('Ninguna regla coincide: el gasto quedaría pendiente de clasificar')
            return

        rule = self.rules[index]
        self.test_result.setText(f'Regla {index + 1}: "{rule["rule"]}" → {rule["category"]}')
        self.select_row(index)

    def select_row(self, row):
        self.table.selectRow(row)
        self.table.scrollToItem(self.table.item(row, self.RULE_COLUMN))

    def get_selected_rows(self):
        # selectedIndexes returns one index per cell, so a row can appear more than once
        return sorted(set([ index.row() for index in self.table.selectedIndexes() ]))
