import csv
from collections import defaultdict
from datetime import datetime

INPUT_FILE = "cashflow.csv"
OUTPUT_FILE = "cashflow_sum.csv"

# (mes, categoria) -> suma
sums = defaultdict(float)
categorias = set()

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f, delimiter="\t")

    for num_linea, row in enumerate(reader, 1):
        try:
            fecha = datetime.strptime(row[0].strip(), "%d/%m/%Y")
            mes = fecha.month
            categoria = row[2].strip()

            valor = row[5].strip().replace(",", "")
            importe = float(valor) if valor else 0.0

            sums[(mes, categoria)] += importe
            categorias.add(categoria)

        except (ValueError, IndexError) as e:
            print(f"Error en línea {num_linea}: {e}")
            continue

# Crear tabla:
# Categoria | 1 | 2 | 3 | ... | 12
with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")

    # Cabecera
    writer.writerow(["Categoria"] + [str(mes) for mes in range(1, 13)])

    # Una fila por categoría
    for categoria in sorted(categorias):
        fila = [categoria]

        for mes in range(1, 13):
            if (mes, categoria) in sums:
                fila.append(f"{sums[(mes, categoria)]:.2f}")
            else:
                fila.append("")

        writer.writerow(fila)
