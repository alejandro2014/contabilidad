from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QToolTip, QWidget

from src.widgets.charts.ChartPalette import ChartPalette

class Treemap(QWidget):
    # Soft colors, so the dark labels are easy to read on all of them
    COLORS = [ '#a8c8e8', '#f4c2a1', '#b5dfc4', '#f6dc9b', '#f2bcd0', '#c9c1ec',
               '#a9dcdc', '#e6c7b0', '#d4e4a8', '#f0b8b0', '#bcd0f0', '#dcc8e0' ]
    TEXT_COLOR = '#2b2b2b'
    BORDER_COLOR = '#ffffff'
    PADDING = 6

    def __init__(self, *args, **kwargs):
        super(Treemap, self).__init__(*args, **kwargs)

        self.chart_palette = ChartPalette()
        # (category, amount, percentage) of each piece, biggest first
        self.items = []

        self.setMinimumSize(150, 150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

    def set_data(self, values):
        # Only positive amounts take space: a category with more refunds than expenses can't be drawn
        positive = [ (category, amount) for category, amount in values if amount is not None and amount > 0 ]
        total = sum([ amount for category, amount in positive ])

        positive.sort(key = lambda value: value[1], reverse = True)
        self.items = [ (category, amount, amount / total * 100) for category, amount in positive ]

        self.update()

    def split_rectangles(self, rect):
        # Squarified treemap: pieces are grouped in rows along the shortest side, adding pieces
        # to a row while that keeps them closer to squares, so the layout doesn't just alternate cuts
        rectangles = []
        total = sum([ amount for category, amount, percentage in self.items ])

        if total == 0 or rect.width() <= 0 or rect.height() <= 0:
            return rectangles

        scale = rect.width() * rect.height() / total
        row = []

        for category, amount, percentage in self.items:
            area = amount * scale
            side = min(rect.width(), rect.height())

            if len(row) > 0 and self.worst_ratio(row + [ area ], side) > self.worst_ratio(row, side):
                rect = self.lay_out_row(row, rect, rectangles)
                row = []

            row.append(area)

        self.lay_out_row(row, rect, rectangles)

        return rectangles

    def worst_ratio(self, row, side):
        # Highest width/height (or height/width) ratio of the pieces of a row laid along that side
        row_area = sum(row)
        return max([ max(side * side * area / (row_area * row_area), row_area * row_area / (side * side * area)) for area in row ])

    def lay_out_row(self, row, rect, rectangles):
        # Places the row along the shortest side of the space left and returns what remains
        row_area = sum(row)

        if rect.width() >= rect.height():
            row_width = row_area / rect.height()
            top = rect.top()
            for area in row:
                piece_height = area / row_width
                rectangles.append(QRectF(rect.left(), top, row_width, piece_height))
                top += piece_height
            return QRectF(rect.left() + row_width, rect.top(), rect.width() - row_width, rect.height())

        row_height = row_area / rect.width()
        left = rect.left()
        for area in row:
            piece_width = area / row_height
            rectangles.append(QRectF(left, rect.top(), piece_width, row_height))
            left += piece_width
        return QRectF(rect.left(), rect.top() + row_height, rect.width(), rect.height() - row_height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if len(self.items) == 0:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 'Sin gastos')
            return

        for index, (rect, (category, amount, percentage)) in enumerate(zip(self.split_rectangles(QRectF(self.rect())), self.items)):
            painter.setPen(QPen(QColor(self.BORDER_COLOR), 2))
            painter.setBrush(QColor(self.COLORS[index % len(self.COLORS)]))
            painter.drawRect(rect)

            self.draw_label(painter, rect, category, percentage)

    def draw_label(self, painter, rect, category, percentage):
        text_rect = rect.adjusted(self.PADDING, self.PADDING, -self.PADDING, -self.PADDING)

        name_font = QFont()
        name_font.setBold(True)
        name_metrics = QFontMetrics(name_font)

        # Pieces too small for the text only show it in the tooltip
        if text_rect.height() < name_metrics.height() or text_rect.width() < name_metrics.averageCharWidth() * 3:
            return

        painter.setPen(QColor(self.TEXT_COLOR))
        painter.setFont(name_font)
        name = name_metrics.elidedText(category, Qt.TextElideMode.ElideRight, int(text_rect.width()))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, name)

        if text_rect.height() >= name_metrics.height() * 2:
            painter.setFont(QFont())
            percentage_rect = text_rect.adjusted(0, name_metrics.height(), 0, 0)
            painter.drawText(percentage_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, f'{percentage:.1f} %')

    def mouseMoveEvent(self, event):
        for rect, (category, amount, percentage) in zip(self.split_rectangles(QRectF(self.rect())), self.items):
            if rect.contains(event.position()):
                text = f'{category}\n{self.chart_palette.format_amount(amount)} ({percentage:.1f} %)'
                QToolTip.showText(event.globalPosition().toPoint(), text, self)
                return

        QToolTip.hideText()
