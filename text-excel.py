import pandas as pd

def extract_data_from_xls(xls_name):
    df = pd.read_excel(xls_name)

    rows_number = df.shape[0]

    df = df[4 : rows_number-1]
    df.columns = ['date', 'category', 'subcategory', 'description', 'comment', 'amount']
    df = df.drop(['comment'], axis=1)

    return [ {
        'date': str(r['date'].date()),
        'category': r['category'],
        'subcategory': r['subcategory'],
        'description': r['description'],
        'amount': float(r['amount'])
    } for _, r in df.iterrows() ]

expenses = extract_data_from_xls('2301.xls')

for expense in expenses:
    print(expense)