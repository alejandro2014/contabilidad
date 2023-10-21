DROP TABLE IF EXISTS expenses;
CREATE TABLE expenses (
    date CHAR(8) NOT NULL,
    title STRING NOT NULL,
    amount FLOAT NOT NULL,
    category STRING NULL,
    subcategory STRING NULL,
    category_src STRING NULL,
    subcategory_src STRING NULL,
    category_suggested STRING NULL,
    subcategory_suggested STRING NULL,
    PRIMARY KEY (date, title, amount)
);

DROP TABLE IF EXISTS expenses_not_classified;
CREATE TABLE expenses_not_classified (
    date_record CHAR(8) NOT NULL,
    concept STRING NOT NULL,
    category STRING NOT NULL,
    subcategory STRING NOT NULL,
    quantity FLOAT NOT NULL,
    PRIMARY KEY (date_record, concept, quantity)
);

DROP TABLE IF EXISTS expenses_classified;
CREATE TABLE expenses_classified (
    date_record CHAR(8) NOT NULL,
    concept STRING NOT NULL,
    quantity FLOAT NOT NULL,
    type VARCHAR NULL,
    PRIMARY KEY (date_record, concept, quantity)
);

DROP TABLE IF EXISTS expense_types;
CREATE TABLE expense_types (
    category VARCHAR NOT NULL PRIMARY KEY,
    comment VARCHAR NULL
);
