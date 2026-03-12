DROP TABLE IF EXISTS expenses;
CREATE TABLE expenses (
    hash CHAR(10) NOT NULL,
    date_record CHAR(8) NOT NULL,
    concept STRING NOT NULL,
    amount FLOAT NOT NULL,
    category1 VARCHAR NULL,
    category2 VARCHAR NULL,
    tag1 VARCHAR NULL,
    tag2 VARCHAR NULL,
    PRIMARY KEY(hash)
);

DROP TABLE IF EXISTS files_loaded;
CREATE TABLE files_loaded (
    hash CHAR(10) NOT NULL,
    file_name VARCHAR(1000),
    date_loaded CHAR(26) NOT NULL,
    PRIMARY KEY(hash)
);

DROP TABLE IF EXISTS rules;
CREATE TABLE rules (
    category VARCHAR(100),
    rule VARCHAR(200),
    PRIMARY KEY(category, rule)
);

DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    name VARCHAR(100) NOT NULL,
    description VARCHAR(300) NULL,
    PRIMARY KEY (name)
);
-------------------------------------------------------
DROP TABLE IF EXISTS file_loader_values;
CREATE TABLE file_loader_values (
    reader_type CHAR(3) NOT NULL,
    has_header BOOLEAN NOT NULL,
    field_name_prefix VARCHAR NOT NULL,
    separator CHAR(1) NOT NULL,
    date_position INTEGER NOT NULL,
    concept_position INTEGER NOT NULL,
    value_position INTEGER NOT NULL
);

INSERT INTO file_loader_values (reader_type, has_header, field_name_prefix, separator, date_position, concept_position, value_position) VALUES ('csv', 'false', 'field_', '\t', 0, 3, 5);
