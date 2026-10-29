from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout

from src.dialogs.WidgetCreator import WidgetCreator

class NotesDialog(QDialog):
    # The note and the tags of one or several movements. With several, they all get the same ones
    def __init__(self, parent, expenses, existing_tags):
        super(NotesDialog, self).__init__(parent)

        self.setWindowTitle('Notas y etiquetas')
        self.resize(500, 200)
        self.setModal(True)

        widget_creator = WidgetCreator()

        # Starts with the ones of the first movement, so a single one can be edited
        first = expenses[0]

        if len(expenses) == 1:
            title = f'{first.title} ({first.amount} €)'
        else:
            title = f'{len(expenses)} movimientos: todos tendrán esta nota y estas etiquetas'

        self.note_textbox = QLineEdit(first.note or '')
        self.note_textbox.setPlaceholderText('Texto libre')

        self.tags_textbox = QLineEdit(', '.join(first.tags))
        self.tags_textbox.setPlaceholderText('Separadas por comas, p. ej.: Viaje Roma, Regalos')

        note_layout = QHBoxLayout()
        note_layout.addWidget(QLabel('Nota:'))
        note_layout.addWidget(self.note_textbox)

        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel('Etiquetas:'))
        tags_layout.addWidget(self.tags_textbox)

        existing_label = QLabel('Etiquetas existentes: ' + (', '.join(existing_tags) if len(existing_tags) > 0 else 'ninguna'))
        existing_label.setWordWrap(True)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(widget_creator.create_button('Aceptar', 'ok', self.accept))
        buttons_layout.addWidget(widget_creator.create_button('Cancelar', 'cancel', self.reject))

        layout = QVBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addLayout(note_layout)
        layout.addLayout(tags_layout)
        layout.addWidget(existing_label)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def note(self):
        return self.note_textbox.text()

    def tags(self):
        return self.tags_textbox.text()
