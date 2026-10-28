# Contabilidad

Desktop app to keep track of personal expenses. It loads bank statements, classifies each movement into an expense type (automatically by rules, or by hand), and shows the results as tables, a cash flow and a dashboard of charts.

Built with Python, PySide6 (Qt 6 and Qt Charts) and SQLite.

## Getting started

```sh
pip install -r requirements.txt
make run            # or: python accountancy-manager.py
```

Run it from the repository root: paths such as `src/config/db/accountancy.db` are relative to it. The database is created automatically the first time, with the tables from `src/config/db/create_database.sql` and the classification rules from `src/config/db/initial-rules.json`.

## Using the app

### Gastos

- **Cargar fichero**: imports a bank statement (`.xls`, see below). Every movement is checked against the classification rules: the ones that match get their expense type, the rest stay pending. Movements already in the database (same date, concept and amount) are ignored.
- **Clasificar pendientes**: table of the movements without an expense type, to classify them by hand.
- **Salir**

### Ver

- **Ver tabla**: classified movements, with date range and text filters. They can be grouped by month and/or expense type, and selected ones can be unclassified.
- **Ver graficos**: the dashboard (the screen shown on start-up), for the selected date range:
  - Quick periods: this month, last month, last 3 and 12 months, this year, last year.
  - Total spent, and cards with incomes, savings, savings rate, monthly average, top category, month with the most spending, and how many movements in the range are still pending (the figures are incomplete until they are classified).
  - Expenses by category (the smallest ones are grouped into "Otros").
  - Incomes and expenses per month.
  - Monthly evolution of the 5 categories with the most spending.
  - The 25 biggest expenses, with repeated ones (same concept, type and amount) in a single row: `937,58 € (10)`.
- **Flujo de caja**: incomes, expenses and balance per month for a year, grouped by the bank category or by expense type. It can be exported to CSV.

### Configuracion

- **Tipos de gastos**: add, edit and delete expense types. Two flags change how a type is counted:
  - *Ingreso*: it is an income (e.g. payroll), shown as income and left out of the expenses.
  - *No computar*: it is neither an income nor an expense (e.g. transfers to a savings account), left out of every sum.
- **Reglas de clasificación**: ordered list of rules (text in the concept → expense type). The first rule that matches wins.

## Supported files

Only `.xls` bank statements with the columns `F. VALOR, CATEGORÍA, SUBCATEGORÍA, DESCRIPCIÓN, COMENTARIO, IMPORTE (€), SALDO (€)`. The header row is looked for by its `F. VALOR` cell, so any lines above it are skipped.

Amounts are stored as in the bank: expenses are negative and incomes positive. The screens show the expenses as positive amounts.

## Project layout

```
accountancy-manager.py      Entry point of the desktop app
MainWindow.py               Main window and menus
DateConverter.py            Conversions between the stored dates (YYYYMMDD) and the shown ones
src/
  screens/                  Full screens (tables, dashboard, cash flow)
  dialogs/                  Configuration and load dialogs
  widgets/                  Filters, summary cards, charts and tables
  services/                 Business logic; formatters/ turn query rows into what the widgets show
  dao/                      SQL generation (SqlGenerator) and SQLite access
  events/                   ListenersPool: widgets send events to each other by node id
  model/                    Expense model
  config/                   Database schema and initial rules, table column definitions, icons
test/                       Unit tests (unittest), same folders as src/
```

## Tests

```sh
make test           # or: python -m unittest discover -s test -t . -b
```

The output of the app is hidden unless a test fails. To run a single module or test:

```sh
python -m unittest test.services.test_chart_formatter
python -m unittest test.services.test_chart_formatter.ChartFormatterTestCase.test__format_kpis
```

The tests never touch `accountancy.db`: the database is mocked, or a temporary one is created. The widget tests run Qt without opening any window.
