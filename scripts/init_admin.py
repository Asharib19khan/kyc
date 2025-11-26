"""
Script to create the first admin user on production
Run this ONCE after deploying to initialize the admin account
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_conn
from app.api.auth import hash_password

def create_admin_user():
    conn = get_conn()
    cursor = conn.cursor()
    
    # Check if admin already exists
    existing = cursor.execute("SELECT * FROM Admins WHERE username = ?", ("Asharib",)).fetchone()
    if existing:
        print("❌ Admin user 'Asharib' already exists!")
        conn.close()
        return
    
    # Create admin user
    username = "Asharib"
    password = "mywordislaw"
    full_name = "Asharib Khan"
    email = "asharib@neobank.com"
    
    hashed_password = hash_password(password)
    
    cursor.execute(
        "INSERT INTO Admins (username, password_hash, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
        (username, hashed_password, full_name, email, "super_admin")
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ Admin user '{username}' created successfully!")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Full Name: {full_name}")

if __name__ == "__main__":
    create_admin_user()
