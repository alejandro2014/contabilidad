-- Amounts as integer cents, so the sums are exact.
-- The expense type of the expenses and rules is a foreign key: renaming a type renames it everywhere,
-- deleting it leaves its expenses pending and deletes its rules.
-- The columns that were never filled (subcategory, category_suggested, subcategory_suggested) are dropped.

-- Types used by expenses or rules but missing in expense_types, so no data is lost
INSERT OR IGNORE INTO expense_types (category) SELECT category FROM expenses WHERE category IS NOT NULL;
INSERT OR IGNORE INTO expense_types (category) SELECT category FROM rules;

CREATE TABLE expenses_new (
    id CHAR(36) NOT NULL,
    date CHAR(8) NOT NULL,
    title STRING NOT NULL,
    amount INTEGER NOT NULL,
    category VARCHAR NULL REFERENCES expense_types (category) ON UPDATE CASCADE ON DELETE SET NULL,
    category_src STRING NULL,
    subcategory_src STRING NULL,
    PRIMARY KEY (date, title, amount)
);

INSERT INTO expenses_new (id, date, title, amount, category, category_src, subcategory_src)
    SELECT id, date, title, CAST(ROUND(amount * 100) AS INTEGER), category, category_src, subcategory_src FROM expenses;

DROP TABLE expenses;
ALTER TABLE expenses_new RENAME TO expenses;

CREATE INDEX expenses_id ON expenses (id);

CREATE TABLE rules_new (
    priority INTEGER NOT NULL PRIMARY KEY,
    rule VARCHAR NOT NULL,
    category VARCHAR NOT NULL REFERENCES expense_types (category) ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT INTO rules_new (priority, rule, category) SELECT priority, rule, category FROM rules;

DROP TABLE rules;
ALTER TABLE rules_new RENAME TO rules;
