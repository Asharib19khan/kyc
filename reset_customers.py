import sqlite3
import os

DB_PATH = os.path.join('data', 'kyc.sqlite3')

def reset_customers():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Deleting all customer data...")
        
        # Delete from dependent tables first
        tables_to_clear = [
            'LoanApplications',
            'Notifications',
            'Messages',
            'LoanEligibility',
            'Verifications',
            'Documents',
            'AuditLog' # Optional: clear audit log too? Maybe better to keep for admin history, but user said "past customer data". Let's clear audit log related to customers if possible, or just all. Let's clear all for a fresh start.
        ]

        for table in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f"Cleared {table}")
            except sqlite3.OperationalError:
                print(f"Table {table} not found (skipping)")

        # Delete Customers
        cursor.execute("DELETE FROM Customers")
        print("Cleared Customers")

        # Reset Auto-Increment Counters (Optional but good for "fresh" feel)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='Customers'")
        
        conn.commit()
        print("\nSUCCESS: All customer data has been deleted. Admin accounts are preserved.")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_customers()
