import pandas as pd
import os
from app.db import get_conn

EXPORT_DIR = "powerbi_data"

def export_to_csv():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = get_conn()
    
    tables = ["Customers", "Verifications", "LoanEligibility", "Transactions", "FinancialHealth"]
    
    print(f"Exporting data to '{EXPORT_DIR}/'...")
    
    for table in tables:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            path = os.path.join(EXPORT_DIR, f"{table}.csv")
            df.to_csv(path, index=False)
            print(f"✔ Exported {table}.csv ({len(df)} rows)")
        except Exception as e:
            print(f"⚠ Could not export {table}: {e}")
            
    conn.close()
    print("\nDone! Open Power BI and import these CSV files.")

if __name__ == "__main__":
    export_to_csv()
