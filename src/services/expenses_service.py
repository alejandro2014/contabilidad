from src.dao.expenses_dao import ExpensesDao

class ExpensesService:
    def __init__(self, dao=None):
        self.dao = ExpensesDao() if dao is None else dao

    def load_expenses(self, expenses):
        return self.dao.load_expenses(expenses)
    
    def get_pending_expenses(self, filter=None, sort_by=None):
        return self.dao.get_pending_expenses(filter, sort_by)
    
    def classify_expenses(self, expense_ids, category):
        for expense_id in expense_ids:
            self.dao.update_classified_expense(expense_id, category)

    def unclassify_expenses(self, expense_ids):
        for expense_id in expense_ids:
            self.dao.update_unclassified_expense(expense_id)

    def get_classified_expenses(self, filter=None, sort_by=None):
        return self.dao.get_classified_expenses(filter, sort_by)

    def get_classified_expenses_by_month(self):
        return self.dao.get_classified_expenses_by_month()

    def get_classified_expenses_by_type(self):
        return self.dao.get_classified_expenses_by_type()

    def get_classified_expenses_by_type_and_month(self):
        return self.dao.get_classified_expenses_by_type_and_month()
    
    def update_notes_and_tags(self, expense_ids, note, tags):
        # A tag that already exists keeps how it is written
        existing_tags = { tag.casefold(): tag for tag in self.dao.get_tags() }
        tags = [ existing_tags.get(tag.casefold(), tag) for tag in self.clean_tags(tags) ]

        self.dao.update_notes_and_tags(expense_ids, self.clean_note(note), tags)

    def clean_note(self, note):
        note = (note or '').strip()

        return note if note != '' else None

    def clean_tags(self, tags):
        # Typed separated by commas. The same tag with other case or spaces is only once
        cleaned = {}

        for tag in tags.split(',') if isinstance(tags, str) else tags:
            tag = ' '.join(tag.split())

            if tag != '' and tag.casefold() not in cleaned:
                cleaned[tag.casefold()] = tag

        return list(cleaned.values())

    def get_tags(self):
        return self.dao.get_tags()

    def get_tag_totals(self, filter=None):
        return self.dao.get_tag_totals(filter)

    def get_classified_expenses_count(self):
        return self.dao.get_classified_expenses_count()

    def get_pending_expenses_count(self):
        return self.dao.get_pending_expenses_count()

    def get_expenses_date_range(self):
        return self.dao.get_expenses_date_range()