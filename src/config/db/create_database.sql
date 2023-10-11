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
