import csv

import pandas as pd

class ExportService:
    def export_table(self, file_name, header, rows, sheet_name='Movimientos'):
        # The format is the one of the extension: Excel (.xlsx) or CSV
        if file_name.lower().endswith('.xlsx'):
            self.export_sheets(file_name, { sheet_name: (header, rows) })
            return

        with open(file_name, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, lineterminator='\n')

            writer.writerow(header)
            writer.writerows([ [ '' if value is None else value for value in row ] for row in rows ])

    def export_sheets(self, file_name, sheets):
        # A sheet for each table: { name: (header, rows) }. Excel doesn't allow longer sheet names
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            for name, (header, rows) in sheets.items():
                pd.DataFrame(rows, columns=header).to_excel(writer, sheet_name=name[:31], index=False)
