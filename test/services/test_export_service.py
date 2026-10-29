import os
import tempfile
import unittest

import pandas as pd

from src.services.ExportService import ExportService

class ExportServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.export_service = ExportService()

        self.header = [ 'Fecha', 'Concepto', 'Cantidad' ]
        self.rows = [ [ '05/01/2026', 'Pago en MERCADONA, MADRID', -30.5 ], [ '06/01/2026', 'Café', None ] ]

    def tearDown(self):
        self.directory.cleanup()

    def test__export_table__csv(self):
        file_name = os.path.join(self.directory.name, 'movimientos.csv')

        self.export_service.export_table(file_name, self.header, self.rows)

        with open(file_name, encoding='utf-8') as f:
            self.assertEqual('Fecha,Concepto,Cantidad\n05/01/2026,"Pago en MERCADONA, MADRID",-30.5\n06/01/2026,Café,\n', f.read())

    def test__export_table__excel_with_numbers(self):
        file_name = os.path.join(self.directory.name, 'movimientos.xlsx')

        self.export_service.export_table(file_name, self.header, self.rows)

        df = pd.read_excel(file_name, sheet_name='Movimientos')
        self.assertEqual(self.header, list(df.columns))
        self.assertEqual(-30.5, df['Cantidad'][0])

    def test__export_sheets__one_per_table(self):
        file_name = os.path.join(self.directory.name, 'panel.xlsx')

        self.export_service.export_sheets(file_name, { 'Resumen': ([ 'Dato', 'Valor' ], [ [ 'Gastos', 10.0 ] ]), 'Categorías': ([ 'Tipo', 'Gasto' ], []) })

        self.assertEqual([ 'Resumen', 'Categorías' ], list(pd.read_excel(file_name, sheet_name=None).keys()))
