-- Types of the money that goes to a savings account (e.g. "Traspaso emitido a"), shown in the savings chart.
-- Like the not computed ones, they are neither an income nor an expense
ALTER TABLE expense_types ADD COLUMN savings BOOLEAN DEFAULT FALSE;

-- The type of the transfers to the savings account in the initial rules
UPDATE expense_types SET savings = TRUE WHERE category = 'Cuenta ahorro';
