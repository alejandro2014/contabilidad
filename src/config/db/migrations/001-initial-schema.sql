-- Schema of the databases created before the versioned migrations
CREATE TABLE expenses (
    id CHAR(36) NOT NULL,
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

CREATE INDEX expenses_id ON expenses (id);

CREATE TABLE expense_types (
    category VARCHAR NOT NULL PRIMARY KEY,
    comment VARCHAR NULL,
    income BOOLEAN DEFAULT FALSE,
    not_computed BOOLEAN DEFAULT FALSE
);

CREATE TABLE rules (
    priority INTEGER NOT NULL PRIMARY KEY,
    rule VARCHAR NOT NULL,
    category VARCHAR NOT NULL
);
