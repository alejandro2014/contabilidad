from PySide6.QtCharts import QChart
from PySide6.QtGui import QColor, QGuiApplication, QPalette

class ChartPalette:
    # Fixed order of the categorical colors, tested to be told apart with color blindness. A ninth category
    # never gets a new color, it is added to "Otros"
    SERIES = [ '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948' ]
    OTHERS = '#a3a29c'
    OTHERS_NAME = 'Otros'

    INCOME = '#1baf7a'
    EXPENSE = '#e34948'

    # Status colors, only for good or bad values and always together with a sign or a text
    GOOD = '#0ca30c'
    CRITICAL = '#d03b3b'
    WARNING = '#c98500'

    def is_dark(self):
        # Qt follows the light or dark mode of the system, and the palette of the app changes with it
        return QGuiApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128

    def apply_theme(self, chart):
        # The charts don't follow the system by themselves. The theme recolors the series already in the
        # chart, so it is applied before adding them
        chart.setTheme(QChart.ChartTheme.ChartThemeDark if self.is_dark() else QChart.ChartTheme.ChartThemeLight)

    def background_color(self, chart):
        # The themes paint the background with a gradient, so its own color is not the one seen
        brush = chart.backgroundBrush()
        gradient = brush.gradient()

        return brush.color() if gradient is None or len(gradient.stops()) == 0 else gradient.stops()[0][1]

    def category_colors(self, categories, others_name=OTHERS_NAME):
        colors = {}

        for i, category in enumerate(categories):
            color = self.OTHERS if category == others_name or i >= len(self.SERIES) else self.SERIES[i]
            colors[category] = QColor(color)

        return colors

    def format_amount(self, amount):
        # Spanish format: 1.234,56 €
        text = f'{amount:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        return f'{text} €'
