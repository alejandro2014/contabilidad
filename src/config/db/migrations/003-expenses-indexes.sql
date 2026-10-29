-- Every dashboard query filters the expenses by type and date range
CREATE INDEX expenses_date ON expenses (date);
CREATE INDEX expenses_category_date ON expenses (category, date);
