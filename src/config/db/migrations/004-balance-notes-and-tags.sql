-- Balance of the account after each movement (the SALDO column of the statements), in cents. The movements
-- loaded before this version don't have it until their statement is loaded again
ALTER TABLE expenses ADD COLUMN balance INTEGER NULL;

-- Free text about a movement
ALTER TABLE expenses ADD COLUMN note VARCHAR NULL;

-- The tags reference the movements by id, so it has to be unique
DROP INDEX expenses_id;
CREATE UNIQUE INDEX expenses_id ON expenses (id);

-- Tags of the movements (e.g. a trip), several per movement
CREATE TABLE expense_tags (
    expense_id CHAR(36) NOT NULL REFERENCES expenses (id) ON DELETE CASCADE,
    tag VARCHAR NOT NULL,
    PRIMARY KEY (expense_id, tag)
);

CREATE INDEX expense_tags_tag ON expense_tags (tag);
