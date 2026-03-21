class ComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super().__init__()

        self.ComboBoxService = ComboBoxService()

        combo_month = self.create_combobox('Mes', 'get_months')
        combo_year = self.create_combobox('Año', 'get_years')
        combo_categories = self.create_combobox('Tipo de gasto', 'get_categories')

        hbox1 = QtWidgets.QHBoxLayout()
        self.add_combo(hbox1, combo_month)
        self.add_combo(hbox1, combo_year)
        self.add_combo(hbox1, combo_categories)

        vlayout = QtWidgets.QVBoxLayout()

        button = QtWidgets.QPushButton("Click me!")

        hbox2 = QtWidgets.QVBoxLayout()
        #hbox2.addWidget(button)

        implementationLabel = QtWidgets.QLabel("&Implementation file name:")
        implementationLineEdit = QtWidgets.QLineEdit()
        implementationLabel.setBuddy(implementationLineEdit)

        hbox2.addWidget(implementationLabel)
        hbox2.addWidget(implementationLineEdit)

        vlayout.addLayout(hbox1)
        vlayout.addLayout(hbox2)

        self.setLayout(vlayout)

    def create_combobox(self, label_string, method_name):
        label = QtWidgets.QLabel(label_string + ':')
        combo = QtWidgets.QComboBox(self)
        values = getattr(self.ComboBoxService, method_name)()

        for value in values:
            combo.addItem(value)

        return {
            'combo': combo,
            'label': label
        }

    def add_combo(self, layout, combo):
        layout.addWidget(combo['label'])
        layout.addWidget(combo['combo'])
