DROP TABLE IF EXISTS expenses;
CREATE TABLE expenses (
    date_record CHAR(8) NOT NULL,
    concept VARCHAR NOT NULL,
    amount FLOAT NOT NULL,
    total_amount FLOAT NOT NULL,
    tag1 VARCHAR NULL,
    tag2 VARCHAR NULL,
    category1 VARCHAR NULL,
    category2 VARCHAR NULL,
    category_suggested VARCHAR NULL,
    subcategory_suggested VARCHAR NULL,
    file_hash VARCHAR NOT NULL,
    PRIMARY KEY (date_record, concept, amount)
);

DROP INDEX IF EXISTS expenses_id;
CREATE INDEX expenses_id ON expenses (id);

DROP TABLE IF EXISTS expenses_not_classified;
CREATE TABLE expenses_not_classified (
    date_record CHAR(8) NOT NULL,
    concept VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    subcategory VARCHAR NOT NULL,
    quantity FLOAT NOT NULL,
    PRIMARY KEY (date_record, concept, quantity)
);

DROP TABLE IF EXISTS expenses_classified;
CREATE TABLE expenses_classified (
    date_record CHAR(8) NOT NULL,
    concept VARCHAR NOT NULL,
    quantity FLOAT NOT NULL,
    type VARCHAR NULL,
    PRIMARY KEY (date_record, concept, quantity)
);

DROP TABLE IF EXISTS expense_types;
CREATE TABLE expense_types (
    category VARCHAR NOT NULL PRIMARY KEY,
    comment VARCHAR NULL,
    positive BOOLEAN DEFAULT FALSE
);
