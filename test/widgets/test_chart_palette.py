import unittest

from src.widgets.charts.ChartPalette import ChartPalette

class ChartPaletteTestCase(unittest.TestCase):
    def setUp(self):
        self.chart_palette = ChartPalette()

    def test__format_amount__spanish_format(self):
        self.assertEqual('1.234.567,89 €', self.chart_palette.format_amount(1234567.891))
        self.assertEqual('-937,58 €', self.chart_palette.format_amount(-937.58))
        self.assertEqual('0,00 €', self.chart_palette.format_amount(0))

    def test__category_colors__fixed_order(self):
        colors = self.chart_palette.category_colors([ 'Alquiler', 'Comida' ])

        self.assertEqual(ChartPalette.SERIES[0], colors['Alquiler'].name())
        self.assertEqual(ChartPalette.SERIES[1], colors['Comida'].name())

    def test__category_colors__others_are_gray(self):
        colors = self.chart_palette.category_colors([ 'Alquiler', ChartPalette.OTHERS_NAME ])

        self.assertEqual(ChartPalette.OTHERS, colors[ChartPalette.OTHERS_NAME].name())

    def test__category_colors__no_new_colors_after_the_palette(self):
        categories = [ f'Categoría {i}' for i in range(len(ChartPalette.SERIES) + 2) ]

        colors = self.chart_palette.category_colors(categories)

        self.assertEqual(ChartPalette.SERIES[-1], colors[categories[len(ChartPalette.SERIES) - 1]].name())
        self.assertEqual(ChartPalette.OTHERS, colors[categories[-1]].name())
