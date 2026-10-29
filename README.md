# Contabilidad

Desktop app to keep track of personal expenses. It loads bank statements, classifies each movement into an expense type (automatically by rules, or by hand), and shows the results as tables, a cash flow and a dashboard of charts.

Built with Python, PySide6 (Qt 6 and Qt Charts) and SQLite.

## Getting started

```sh
pip install -r requirements.txt
make run            # or: python accountancy-manager.py
```

Run it from the repository root: paths such as `src/config/db/accountancy.db` are relative to it. The database is created automatically the first time, with the tables from `src/config/db/create_database.sql` and the classification rules from `src/config/db/initial-rules.json`.

Before every import and every schema migration, the database is copied to `src/config/db/backups/accountancy-YYYYMMDD-HHMMSS.db`. Only the last 10 copies are kept.

## Using the app

### Gastos

- **Cargar fichero**: imports a bank statement (`.xls`, see below). Every movement is checked against the classification rules: the ones that match get their expense type, the rest stay pending. Movements already in the database (same date, concept and amount) are ignored. The whole file is loaded in a single transaction: if anything fails, nothing is loaded.
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

- **Tipos de gastos**: add, edit and delete expense types. Renaming a type also renames it in its movements and rules. Deleting a type that is in use asks whether to move its movements and rules to another type, or to leave the movements pending again (and delete its rules). Two flags change how a type is counted:
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

## TODO

### Database

- [ ] Versioned migrations (`PRAGMA user_version` + numbered scripts) instead of the `add_*_if_needed` checks, which run on every single query.
- [ ] Open one connection for the life of the app instead of one per query.
- [ ] Store amounts as integer cents instead of `FLOAT`: sums like `0.1 + 0.2` then add up exactly.
- [ ] Foreign keys from `expenses.category` and `rules.category` to `expense_types` (`ON UPDATE CASCADE`), so the database itself keeps them consistent (today `ExpenseTypesService` renames and deletes them by hand).
- [ ] Index on `expenses(date)` and `expenses(category)`: every dashboard query filters by them.
- [ ] Remove or use the columns that are never filled: `subcategory`, `category_suggested`, `subcategory_suggested`.
- [ ] `substr(date, 0, 7)` works only because SQLite treats position 0 as 1: use `substr(date, 1, 6)` like the other queries.
- [ ] Database path configurable (env var or settings file) and independent of the working directory, so the app can be started from anywhere. Same for `src/config/...` paths in `ConfigLoader`.

### Import

- [ ] Support `.xlsx` and `.csv` statements, and other banks: describe each format (header cell, column order, date and amount format) in a JSON file under `src/config/banks/`.
- [ ] Drag and drop a file onto the window to import it, and import several files at once.
- [ ] Preview before importing: how many rows are new, duplicated and auto-classified, with a cancel button.
- [ ] Better duplicate detection: two real, identical movements on the same day (two coffees of 1,50 €) are counted as one. Use the balance column (`SALDO`) to tell them apart.
- [ ] Remember the last folder used in the file dialog.

### Classification

- [ ] Apply the rules to the movements that are already pending ("Reclasificar pendientes"), e.g. after adding a rule.
- [ ] Create a rule straight from the pending table: right click on a movement → "Crear regla con este concepto".
- [ ] Suggest a type for each pending movement from how similar concepts were classified before (fill `category_suggested`), and accept all suggestions with one click.
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

### Dashboard and reports

- [ ] Compare a period with the previous one, or with the same period last year, in the KPI cards (`+12 %`).
- [ ] Click on a chart slice / bar to open the table filtered by that type and month.
- [ ] Average per category vs. current month, to see where the month is going off-track.
- [ ] Net worth: evolution of the balance (`SALDO`) of the account.
- [ ] Export the table view and the dashboard (CSV / Excel / PDF), not just the cash flow.
- [ ] Remember the last date range, screen and window size between sessions (`QSettings`).
- [ ] Notes and tags on movements (e.g. a trip), with totals per tag.

### UI

- [ ] Consistent language: the menus are in Spanish, without accents in some places (`Ver graficos`, `Configuracion`). Use Qt translations or at least fix the texts.
- [ ] Keyboard shortcuts for the main screens and for classifying (`Ctrl+O` import, type ahead in the type combo, `Enter` to classify and move to the next one).
- [ ] Dark mode that follows the system, also in the charts.
- [ ] Show the number of pending movements in the menu (`Clasificar pendientes (12)`) and a button on the "pending" KPI card that opens that screen.
- [ ] Confirmation before deleting rules, and before unclassifying.
- [ ] Remove commented-out code (`#self.view_expenses_table()`, the commented `sql` in `ExpensesDao`) and solve or drop the old `#TODO`s in `ListenersPool` and `Summatory`.

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
