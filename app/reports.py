import pandas as pd
from app.db import get_conn
import os

REPORTS_DIR = 'reports'

def export_verification_report(filename="verification_report.xlsx"):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, filename)
    
    conn = get_conn()
    query = """
    SELECT 
        c.full_name, c.cnic, c.income_range,
        v.status, v.risk_score, v.trust_score, v.verified_by, v.updated_at,
        l.eligibility_status, l.max_limit
    FROM Customers c
    LEFT JOIN Verifications v ON c.id = v.customer_id
    LEFT JOIN LoanEligibility l ON c.id = l.customer_id
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Add summary sheet
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Detailed Data', index=False)
        
        # Summary
        summary = df['status'].value_counts().to_frame("Count")
        summary.to_excel(writer, sheet_name='Summary')
        
    print(f"Report exported to {path}")
    return path

if __name__ == "__main__":
    export_verification_report()
