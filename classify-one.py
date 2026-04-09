import sqlite3

class DbManager:
    def __init__(self):
        self.db = 'db/accountancy.db'

    def update(self, sql):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute(sql)

        conn.commit()

    def get_rows(self, sql):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute(sql)

        return cursor.fetchall()
    
    def get_value(self, sql):
        rows = self.get_rows(sql)

        return rows[0][0]


class DbService:
    def __init__(self):
        self.db = DbManager()

    def update_expenses(self, title, category):
        sql = f"update expenses set tag1 = '{category}' where concept = '{title}'"

        self.db.update(sql)
    
    def get_count_assigned(self):
        return self.db.get_value("SELECT count(*) from expenses where tag1 is not null")

    def get_count_unassigned(self):
        return self.db.get_value("SELECT count(*) from expenses where tag1 is null")

    def get_next_category_to_classify(self):
        sql = f'''
            select a from (
                select 
                    concept a, 
                    count(*) b 
                from expenses 
                where tag1 is null 
                group by concept
            ) order by b desc limit 1;
        '''
        
        return self.db.get_value(sql)

    def get_next_category_records(self, title):
        sql = f"select count(*) from expenses where concept = '{title}'"

        return self.db.get_value(sql)
    
    def print_expenses(self, title):
        sql = f"SELECT * FROM expenses WHERE concept = '{title}'"

        rows = self.db.get_rows(sql)

        for row in rows:
            print(row)

    def get_data_for_date(self, year=None, month=None):
        sql = f"select date_record, concept, tag1, amount from expenses where date_record like '{year}{str(month).zfill(2)}%' order by date_record"

        header = [('Fecha', 'Concepto', 'Categoría', 'Importe')]
        rows = self.db.get_rows(sql)

        return header + rows
    
    def get_category(self, concept):
        sql = f"select tag1 from expenses where concept = '{concept}' limit 1"

        try:
            category = self.db.get_value(sql)
        except IndexError:
            category = None

        return category


service = DbService()

def get_percent_assigned():
    count_assigned = service.get_count_assigned()
    count_unassigned = service.get_count_unassigned()

    return round(count_assigned / (count_assigned + count_unassigned) * 100, 2)

def print_assigned():
    assigned = service.get_count_assigned()
    unassigned = service.get_count_unassigned()
    percent = get_percent_assigned()

    print(f"{assigned}/{assigned + unassigned} ({percent}%)")

def classify():
    while True:
        next_title = service.get_next_category_to_classify()
        records = service.get_next_category_records(next_title)

        service.print_expenses(next_title)

        category = input(f"{next_title} ({records}): ")
        service.update_expenses(next_title, category)

        print_assigned()

def transform_to_csv_lines(rows):
    return [ f"{r[0]}\t{r[1]}\t{r[2]}\t{str(r[3]).replace(',', '').replace('.', ',')}\n" for r in rows ]

def generate_csv(rows, year=None, month=None):
    file_name = f"{year}{str(month).zfill(2)}.csv"

    open(file_name, 'w').writelines(rows)

def generate_month(year=None, month=None):
    data = service.get_data_for_date(year=year, month=month)
    data = transform_to_csv_lines(data)
    generate_csv(data, year=year, month=month)

def generate_year(year=None):
    for month in range(1, 13):
        generate_month(year=year, month=month)

# classify()
#generate_month(year=2025, month=1)
#generate_year(year=2025)

category = service.get_category('Recibo TELEFONICA DE ESPANA, S. A. U.')
print(category)