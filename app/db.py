import sqlite3
import os

DB_PATH = os.path.join('data', 'kyc.sqlite3')
SCHEMA_PATH = os.path.join('app', 'schema.sql')

def get_conn():
    """Returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and performs schema migrations."""
    if not os.path.exists(SCHEMA_PATH):
        print(f"Error: Schema file not found at {SCHEMA_PATH}")
        return

    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()

    conn = get_conn()
    cursor = conn.cursor()
    try:
        # 1. Run base schema (creates tables IF NOT EXISTS)
        cursor.executescript(schema_sql)
        
        # 2. Add LoanEligibility Table (if not in schema.sql yet)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS LoanEligibility (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            risk_score INTEGER,
            income_range TEXT,
            eligibility_status TEXT,
            max_limit INTEGER,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES Customers(id)
        )
        ''')

        # 3. Add AuditLog Table (if not in schema.sql yet)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS AuditLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            admin_user TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 4. Add LoanApplications Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS LoanApplications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            amount INTEGER,
            purpose TEXT,
            monthly_income INTEGER,
            status TEXT DEFAULT 'Pending',
            rejection_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES Customers(id)
        )
        ''')

        # 5. Add Notifications Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            title TEXT,
            message TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES Customers(id)
        )
        ''')

        # 6. Add Messages Table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            sender TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES Customers(id)
        )
        ''')

        # 7. Add new columns to Customers (Migration)
        try:
            cursor.execute("ALTER TABLE Customers ADD COLUMN trust_score INTEGER DEFAULT 0")
        except Exception:
            pass 

        try:
            cursor.execute("ALTER TABLE Customers ADD COLUMN segment TEXT DEFAULT 'Standard'")
        except Exception:
            pass 

        try:
            cursor.execute("ALTER TABLE Admins ADD COLUMN settings TEXT DEFAULT '{}'")
        except Exception:
            pass 

        try:
            cursor.execute("ALTER TABLE LoanEligibility ADD COLUMN income_range TEXT")
        except Exception:
            pass 

        try:
            cursor.execute("ALTER TABLE Customers ADD COLUMN customer_code TEXT UNIQUE")
        except Exception:
            pass 

        # Add date column to Verifications table for tracking verification dates
        try:
            cursor.execute("ALTER TABLE Verifications ADD COLUMN date TIMESTAMP")
            # Populate existing records with updated_at value
            cursor.execute("UPDATE Verifications SET date = updated_at WHERE date IS NULL")
        except Exception:
            pass 

        conn.commit()
        print(f"Database initialized and migrated successfully at {DB_PATH}")
    except sqlite3.Error as e:
        print(f"Database initialization failed: {e}")
    finally:
        conn.close()

# --- CRUD Operations ---

from app import security_utils

# ... (imports)

def insert_customer(full_name, cnic, email, phone, address, income_range, password_hash, trust_score=50, segment="Standard"):
    conn = get_conn()
    cursor = conn.cursor()
    
    # Encrypt Sensitive Data
    enc_cnic = security_utils.encrypt_data(cnic)
    enc_phone = security_utils.encrypt_data(phone)
    enc_address = security_utils.encrypt_data(address)
    
    # Generate Unique Customer Code (8-character alphanumeric)
    import random
    import string
    customer_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Ensure uniqueness
    while cursor.execute("SELECT id FROM Customers WHERE customer_code = ?", (customer_code,)).fetchone():
        customer_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    try:
        cursor.execute(
            "INSERT INTO Customers (full_name, cnic, email, phone, address, income_range, password_hash, trust_score, segment, customer_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (full_name, enc_cnic, email, enc_phone, enc_address, income_range, password_hash, trust_score, segment, customer_code)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        return customer_id, customer_code  # Return both ID and code
    except sqlite3.IntegrityError:
        # Note: Since CNIC is encrypted, uniqueness check might fail if we don't handle it carefully.
        # For this demo, we assume the encrypted string is unique enough (deterministic encryption would be needed for strict unique index, but Fernet is non-deterministic).
        # To keep it simple for the demo, we catch the error.
        raise ValueError("Customer with this CNIC already exists.")
    finally:
        conn.close()

def insert_document(customer_id, doc_type, file_path):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Documents (customer_id, doc_type, file_path) VALUES (?, ?, ?)",
        (customer_id, doc_type, file_path)
    )
    conn.commit()
    conn.close()

def update_verification_status(customer_id, status, risk_score, trust_score, remarks, verified_by):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Verifications 
        SET status = ?, risk_score = ?, trust_score = ?, remarks = ?, verified_by = ?, updated_at = CURRENT_TIMESTAMP, date = CURRENT_TIMESTAMP
        WHERE customer_id = ?
        """,
        (status, risk_score, trust_score, remarks, verified_by, customer_id)
    )
    conn.commit()
    conn.close()

def get_pending_customers():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.full_name, c.cnic, v.status, v.risk_score, v.trust_score, v.remarks, v.updated_at 
        FROM Customers c
        JOIN Verifications v ON c.id = v.customer_id
        WHERE v.status = 'Pending'
    """)
    return cursor.fetchall()

def get_customer_by_id(customer_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        # Convert Row to dict to modify it
        cust = dict(row)
        cust['cnic'] = security_utils.decrypt_data(cust['cnic'])
        cust['phone'] = security_utils.decrypt_data(cust['phone'])
        cust['address'] = security_utils.decrypt_data(cust['address'])
        return cust
    return None

def log_action(action, admin_user, details):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO AuditLog (action, admin_user, details) VALUES (?, ?, ?)",
        (action, admin_user, details)
    )
    conn.commit()
    conn.close()

# --- Loan Logic ---

def init_financials(customer_id, is_demo=False):
    conn = get_conn()
    cursor = conn.cursor()

    if is_demo:
        # Demo User: Inject Fake Data
        cursor.execute(
            "INSERT INTO FinancialHealth (customer_id, spending_score, savings_rate, predicted_balance) VALUES (?, ?, ?, ?)",
            (customer_id, 72, 15.5, 183385.0)
        )
        
        # 2. Transactions
        txs = [
            (customer_id, 761, "Debit", "Transport", "2025-11-18"),
            (customer_id, 13509, "Debit", "Shopping", "2025-11-16"),
            (customer_id, 720, "Debit", "Transport", "2025-11-15"),
            (customer_id, 77511, "Credit", "Salary", "2025-11-14"),
            (customer_id, 64435, "Credit", "Salary", "2025-11-10")
        ]
        cursor.executemany("INSERT INTO Transactions (customer_id, amount, type, category, date) VALUES (?, ?, ?, ?, ?)", txs)
        
    else:
        # Real User: Start with 0
        cursor.execute(
            "INSERT INTO FinancialHealth (customer_id, spending_score, savings_rate, predicted_balance) VALUES (?, ?, ?, ?)",
            (customer_id, 0, 0.0, 0.0)
        )
        # No transactions for real users
        
    conn.commit()
    conn.close()

def get_customer_financials(customer_id):
    conn = get_conn()
    cursor = conn.cursor()
    
    health = cursor.execute("SELECT * FROM FinancialHealth WHERE customer_id=?", (customer_id,)).fetchone()
    transactions = cursor.execute("SELECT * FROM Transactions WHERE customer_id=? ORDER BY date DESC LIMIT 5", (customer_id,)).fetchall()
    
    conn.close()
    return health, transactions

import json

def get_admin_settings(username):
    conn = get_conn()
    cursor = conn.cursor()
    row = cursor.execute("SELECT settings FROM Admins WHERE username = ?", (username,)).fetchone()
    conn.close()
    if row and row[0]:
        try:
            return json.loads(row[0])
        except:
            return {}
    return {}

def update_admin_settings(username, settings):
    conn = get_conn()
    cursor = conn.cursor()
    settings_json = json.dumps(settings)
    cursor.execute("UPDATE Admins SET settings = ? WHERE username = ?", (settings_json, username))
    conn.commit()
    conn.close()

# --- Aliases & Missing Functions for KYC API ---

def save_loan_eligibility(customer_id, risk_score, income_range, status, max_limit):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO LoanEligibility (customer_id, risk_score, income_range, eligibility_status, max_limit) VALUES (?, ?, ?, ?, ?)",
        (customer_id, risk_score, income_range, status, max_limit)
    )
    conn.commit()
    conn.close()

def create_verification_record(customer_id, risk_score, trust_score, remarks):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Verifications (customer_id, risk_score, trust_score, remarks, status) VALUES (?, ?, ?, ?, 'Pending')",
        (customer_id, risk_score, trust_score, remarks)
    )
    conn.commit()
    conn.close()

# Aliases
generate_mock_financials = lambda cust_id: init_financials(cust_id, is_demo=True)
update_verification = update_verification_status
