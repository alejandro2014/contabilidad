import pandas as pd

def extract_expenses_from_xls(xls_name):
    df = pd.read_excel(xls_name)

    rows_number = df.shape[0]

    df = df[4 : rows_number-1]
    df.columns = ['date', 'category', 'subcategory', 'concept', 'comment', 'value']
    df = df.drop(['comment'], axis=1)

    return [ {
        'date': str(r['date'].date()).replace('-', ''),
        'category': r['category'],
        'subcategory': r['subcategory'],
        'concept': r['concept'],
        'value': float(r['value'])
    } for _, r in df.iterrows() ]

def extract_expenses_from_csv(csv_name):
    pass

def extract_expenses(file_name):
    if file_name.endswith('.xls'):
        return extract_expenses_from_xls(file_name)

    if file_name.endswith('.csv'):
        return extract_expenses_from_csv(file_name)
    
    return None
    
expenses = extract_expenses('2301.xls')

for expense in expenses:
    print(expense)