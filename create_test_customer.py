import sqlite3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import security_utils
from app.auth import hash_password

DB_PATH = os.path.join('data', 'kyc.sqlite3')

def create_test_customer():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Customer details
    cnic = "42101-0233667-9"
    password = "123456"
    customer_code = "Y5J5LLPS"
    
    # Encrypt sensitive data
    enc_cnic = security_utils.encrypt_data(cnic)
    enc_phone = security_utils.encrypt_data("03001234567")
    enc_address = security_utils.encrypt_data("Test Address, Karachi")
    
    # Hash password
    password_hash = hash_password(password)
    
    try:
        # Insert Customer
        cursor.execute("""
            INSERT INTO Customers 
            (full_name, cnic, email, phone, address, password_hash, customer_code, trust_score, segment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Test Customer",
            enc_cnic,
            "test@example.com",
            enc_phone,
            enc_address,
            password_hash,
            customer_code,
            75,
            "Standard"
        ))
        
        customer_id = cursor.lastrowid
        print(f"✓ Created customer with ID: {customer_id}")
        
        # Insert Verification Record (Set as Verified)
        cursor.execute("""
            INSERT INTO Verifications 
            (customer_id, status, verified_by, remarks, trust_score)
            VALUES (?, 'Verified', 'System Admin', 'Test account - Auto verified', 75)
        """, (customer_id,))
        print(f"✓ Created verification record (Status: Verified)")
        
        # Insert Loan Eligibility
        cursor.execute("""
            INSERT INTO LoanEligibility 
            (customer_id, risk_score, income_range, eligibility_status, max_limit)
            VALUES (?, ?, ?, ?, ?)
        """, (customer_id, 75, "50000-100000", "Eligible", 100000))
        print(f"✓ Created loan eligibility (Max Limit: PKR 100,000)")
        
        # Insert some mock documents (without actual files)
        doc_types = ['CNIC_Front', 'CNIC_Back', 'Selfie']
        for doc_type in doc_types:
            cursor.execute("""
                INSERT INTO Documents (customer_id, doc_type, file_path)
                VALUES (?, ?, ?)
            """, (customer_id, doc_type, f"uploads/{customer_id}_{doc_type}_test.jpg"))
        print(f"✓ Created {len(doc_types)} document records")
        
        conn.commit()
        print("\n✅ SUCCESS! Test customer created with:")
        print(f"   CNIC: {cnic}")
        print(f"   Password: {password}")
        print(f"   Customer Code: {customer_code}")
        print(f"   Status: Verified")
        print(f"\nYou can now login at http://localhost:5173/login")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_customer()
