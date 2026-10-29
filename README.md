# Contabilidad

Desktop app to keep track of personal expenses. It loads bank statements, classifies each movement into an expense type (automatically by rules, or by hand), and shows the results as tables, a cash flow and a dashboard of charts.

Built with Python, PySide6 (Qt 6 and Qt Charts) and SQLite.

## Getting started

```sh
pip install -r requirements.txt
make run            # or: python accountancy-manager.py
```

It can be started from any folder. The database is `src/config/db/accountancy.db`, or the file in the `ACCOUNTANCY_DB` environment variable:

```sh
ACCOUNTANCY_DB=~/Documents/accountancy.db make run
```

The database is created automatically the first time, with the classification rules from `src/config/db/initial-rules.json` (and their expense types).

The schema is built by the numbered scripts in `src/config/db/migrations/` (`001-initial-schema.sql`, `002-...`). The database stores the number of the last one applied in `PRAGMA user_version`, and on start-up only the newer ones run, each in a single transaction. To change the schema, add the next numbered script. The app keeps a single connection open while it runs, with foreign keys on.

Before every import and every schema migration, the database is copied to `src/config/db/backups/accountancy-YYYYMMDD-HHMMSS.db`. Only the last 10 copies are kept.

The size and place of the window, the last screen, the last date range and the period the dashboard compares with are kept between sessions (`QSettings`: the preferences of the user in macOS).

## Using the app

### Gastos

- **Cargar fichero** (`Ctrl+O`): imports a bank statement (`.xls`, see below). Every movement is checked against the classification rules: the ones that match get their expense type, the rest stay pending. Movements already in the database (same date, concept and amount) are ignored, except that they get their balance if they were loaded before it was stored. The whole file is loaded in a single transaction: if anything fails, nothing is loaded.
- **Clasificar pendientes** (`Ctrl+3`): table of the movements without an expense type, to classify them by hand. The menu shows how many there are: `Clasificar pendientes (12)`. It can be done with the keyboard: typing on the table looks for an expense type (any part of its name), and `Enter` classifies the selected movements and selects the next one.
- **Salir** (`Ctrl+Q`)

### Ver

- **Ver gráficos** (`Ctrl+1`): the dashboard (the screen shown on start-up), for the selected date range:
  - Quick periods: this month, last month, last 3 and 12 months, this year, last year.
  - Total spent, and cards with expenses, incomes, savings, savings rate, monthly average, top category, month with the most spending, and how many movements in the range are still pending (the figures are incomplete until they are classified), with a button to classify them.
  - *Comparar con*: the cards show how much each figure has changed from the previous period (`+12 % vs. periodo anterior`) or from the same period last year. The previous period of whole months (or of this month until today) is the same months before it; of other ranges, the same number of days before it.
  - Expenses by category (the smallest ones are grouped into "Otros"). Clicking a category shows its merchants, and clicking a merchant opens its movements.
  - Incomes and expenses per month. Clicking a bar opens the movements of that month.
  - Monthly evolution of the 5 categories with the most spending. Clicking a point opens the movements of that type and month.
  - The 25 biggest expenses, with repeated ones (same concept, type and amount) in a single row: `937,58 € (10)`. Double clicking one opens its movements.
  - Spending of each type in the last month of the range vs. its monthly average in the 12 months before (only those with movements), the ones going over it first. Double clicking one opens its movements of the month.
  - Balance of the account (`SALDO`) at the end of each month. The movements loaded before it was stored don't have it: load their statements again to fill it.
  - **Exportar**: the dashboard as a PDF (as it is shown, in one page) or as an Excel file with a sheet per chart.
- **Ver tabla** (`Ctrl+2`): classified movements, with date range, text, type and tag filters. They can be grouped by month and/or expense type, or by tag (totals of the expenses of each tag in the date range), and selected ones can be unclassified (after a confirmation).
  - **Notas y etiquetas** (or double click on a movement): a note and tags (e.g. `Viaje Roma`, separated by commas) for the selected movements.
  - **Exportar**: the rows shown, as Excel or CSV.
- **Flujo de caja** (`Ctrl+4`): incomes, expenses and balance per month for a year, grouped by the bank category or by expense type. It can be exported to CSV.

### Configuración

- **Tipos de gastos**: add, edit and delete expense types. Renaming a type also renames it in its movements and rules. Deleting a type that is in use asks whether to move its movements and rules to another type, or to leave the movements pending again (and delete its rules). Two flags change how a type is counted:
  - *Ingreso*: it is an income (e.g. payroll), shown as income and left out of the expenses.
  - *No computar*: it is neither an income nor an expense (e.g. transfers to a savings account), left out of every sum.
- **Reglas de clasificación**: ordered list of rules (text in the concept → expense type). The first rule that matches wins. Deleting rules asks for a confirmation.

The app and its charts follow the light or dark mode of the system, also when it changes while the app is open.

## Supported files

Only `.xls` bank statements with the columns `F. VALOR, CATEGORÍA, SUBCATEGORÍA, DESCRIPCIÓN, COMENTARIO, IMPORTE (€), SALDO (€)`. The header row is looked for by its `F. VALOR` cell, so any lines above it are skipped. The balance (`SALDO`) left by each movement is stored too, for the balance chart.

Amounts are stored as in the bank: expenses are negative and incomes positive. The screens show the expenses as positive amounts. They are stored as integer cents (`-937,58 €` is `-93758`), so the sums are exact, and the queries return them in euros (`amount / 100.0`).

The expense type of the movements and rules is a foreign key to `expense_types`: renaming a type renames it everywhere, and deleting it leaves its movements pending and deletes its rules. The tags of the movements are in `expense_tags` (one row per movement and tag).

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
  config/                   Database migrations and initial rules, table column definitions, icons, paths, settings
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

The tests never touch `accountancy.db`: the database is mocked, or a temporary one is created. The widget tests run Qt without opening any window, and their settings go to a temporary folder.

## TODO

### Import

- [ ] Support `.xlsx` and `.csv` statements, and other banks: describe each format (header cell, column order, date and amount format) in a JSON file under `src/config/banks/`.
- [ ] Drag and drop a file onto the window to import it, and import several files at once.
- [ ] Preview before importing: how many rows are new, duplicated and auto-classified, with a cancel button.
- [ ] Better duplicate detection: two real, identical movements on the same day (two coffees of 1,50 €) are counted as one. Use the balance column (`SALDO`) to tell them apart.
- [ ] Remember the last folder used in the file dialog.

### Classification

- [ ] Apply the rules to the movements that are already pending ("Reclasificar pendientes"), e.g. after adding a rule.
- [ ] Create a rule straight from the pending table: right click on a movement → "Crear regla con este concepto".
- [ ] Suggest a type for each pending movement from how similar concepts were classified before (in a new `category_suggested` column), and accept all suggestions with one click.
- [ ] Rules with more conditions: regex, amount range, sign (income/expense), bank category.
- [ ] Test a rule in the rules dialog: show which movements it would match and which rule currently wins for them.
- [ ] Split a movement into several types (e.g. a supermarket ticket that is part food, part home).
- [ ] Undo the last classification.

### Budgets and savings

- [ ] Monthly budget per expense type (new `budgets` table), with progress bars on the dashboard: spent vs. budget this month, coloured when it goes over.
- [ ] Targets screen: the categories and targets of the savings plan, compared month by month with the actual spending, so the monthly review doesn't have to be done by hand from the cash flow.
- [ ] Savings goals (amount and date, e.g. emergency fund of 6.000 € by Jul 2027): progress from the *No computar* transfers to the savings account, and the projected date at the current rate.
- [ ] Pots: money set aside every month for yearly expenses (vacations, insurance), with what is accumulated and what has been spent from each one.
- [ ] Detect recurring payments (subscriptions, phone, gym): list them with their monthly cost and flag new ones or price rises.
- [ ] Alerts: unusual expenses (much bigger than the average of their type), or a category going over its budget.

### Code quality and tooling

- [ ] Replace `ListenersPool` with Qt signals/slots, so widgets don't depend on string node ids.
- [ ] Services and DAOs: `ExpensesDao` builds its `SqlGenerator()` and `SqliteConnector()` as default arguments, shared by every instance. Inject them like the other services.
- [ ] Consistent file naming (`expenses_service.py` vs `RulesService.py`): pick snake_case modules (PEP 8).
- [ ] Move `MainWindow.py` and `DateConverter.py` into `src/`.
- [ ] Pin the versions in `requirements.txt`, or move to `pyproject.toml` with `uv`.
- [ ] Linting and formatting (`ruff`), type hints and `mypy`, run with `make lint`.
- [ ] Test coverage report (`coverage`), and tests for the dialogs and screens.
- [ ] GitHub Actions running the tests (with `QT_QPA_PLATFORM=offscreen`) on every push.
- [ ] Package the app (`pyinstaller` / `briefcase`) as a macOS `.app`, with its icon.
