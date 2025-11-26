import sqlite3

conn = sqlite3.connect('data/kyc.sqlite3')
cursor = conn.cursor()

try:
    # Add column without UNIQUE constraint since there's existing data
    cursor.execute('ALTER TABLE Customers ADD COLUMN customer_code TEXT')
    conn.commit()
    print('✅ customer_code column added successfully!')
except Exception as e:
    print(f'Error: {e}')
    if 'duplicate column name' in str(e).lower():
        print('✅ Column already exists!')
    
conn.close()
