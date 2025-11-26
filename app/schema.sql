-- Core Tables for KYC System

CREATE TABLE IF NOT EXISTS Customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    cnic TEXT UNIQUE NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    income_range TEXT,
    password_hash TEXT, -- Added for security
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL, -- 'CNIC_Front', 'CNIC_Back', 'Selfie'
    file_path TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES Customers(id)
);

CREATE TABLE IF NOT EXISTS Verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    status TEXT DEFAULT 'Pending', -- 'Pending', 'Verified', 'Rejected'
    risk_score INTEGER DEFAULT 0,
    trust_score INTEGER DEFAULT 0,
    remarks TEXT,
    verified_by TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES Customers(id)
);

CREATE TABLE IF NOT EXISTS LoanEligibility (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    risk_score INTEGER,
    income_group TEXT,
    eligibility_status TEXT, -- 'Auto-Approved', 'Review', 'Rejected'
    max_limit REAL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES Customers(id)
);

CREATE TABLE IF NOT EXISTS Admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'Admin'
);

CREATE TABLE IF NOT EXISTS AuditLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    admin_user TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL, -- 'Credit', 'Debit'
    category TEXT, -- 'Salary', 'Food', 'Transport', etc.
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES Customers(id)
);

CREATE TABLE IF NOT EXISTS FinancialHealth (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    spending_score INTEGER, -- 0-100
    savings_rate INTEGER, -- Percentage
    predicted_balance REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES Customers(id)
);

CREATE TABLE IF NOT EXISTS Locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    latitude REAL,
    longitude REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES Customers(id)
);
