import sqlite3

def update_expenses(title, category):
    sql = f"update expenses set tag1 = '{category}' where concept = '{title}'"

    with sqlite3.connect('db/accountancy.db') as conn:
        cursor = conn.cursor()

        cursor.execute(sql)

        conn.commit()

def get_value(sql):
    with sqlite3.connect('db/accountancy.db') as conn:
        cursor = conn.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()

        return rows[0][0]

def get_rows(sql):
    with sqlite3.connect('db/accountancy.db') as conn:
        cursor = conn.cursor()

        cursor.execute(sql)

        return cursor.fetchall()
    
def get_count_assigned():
    return get_value("SELECT count(*) from expenses where tag1 is not null")

def get_count_unassigned():
    return get_value("SELECT count(*) from expenses where tag1 is null")

def get_next_category_to_classify():
    limit = 0
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
    
    return get_value(sql)

def get_next_category_records(title):
    sql = f"select count(*) from expenses where concept = '{title}'"

    return get_value(sql)

def get_percent_assigned():
    count_assigned = get_count_assigned()
    count_unassigned = get_count_unassigned()

    return round(count_assigned / (count_assigned + count_unassigned) * 100, 2)

def print_assigned():
    assigned = get_count_assigned()
    unassigned = get_count_unassigned()
    percent = get_percent_assigned()

    print(f"{assigned}/{assigned + unassigned} ({percent}%)")

def print_expenses(title):
    sql = f"SELECT * FROM expenses WHERE concept = '{title}'"

    rows = get_rows(sql)

    for row in rows:
        print(row)

while True:
    next_title = get_next_category_to_classify()
    records = get_next_category_records(next_title)

    print_expenses(next_title)

    category = input(f"{next_title} ({records}): ")
    update_expenses(next_title, category)

    print_assigned()