from app.db import init_db, get_conn
from app import auth
import sqlite3

def setup():
    print("--- Setting up Database ---")
    # 1. Initialize DB (Create Tables)
    init_db()
    
    # 2. Create Admin User
    conn = get_conn()
    cursor = conn.cursor()
    
    username = "Asharib"
    password = "admin123"
    password_hash = auth.hash_password(password)
    
    print(f"Creating Admin: {username}")
    
    try:
        cursor.execute(
            "INSERT INTO Admins (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, "Asharib Admin", "Admin")
        )
        conn.commit()
        print("SUCCESS: Admin 'Asharib' created.")
    except sqlite3.IntegrityError:
        print("Admin 'Asharib' already exists. Updating password...")
        cursor.execute(
            "UPDATE Admins SET password_hash = ? WHERE username = ?",
            (password_hash, username)
        )
        conn.commit()
        print("SUCCESS: Admin password updated.")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()

    # 3. Verify
    conn = get_conn()
    user = conn.cursor().execute("SELECT * FROM Admins WHERE username=?", (username,)).fetchone()
    if user:
        print(f"VERIFICATION: User found in DB. Hash starts with: {user['password_hash'][:10]}...")
        if auth.check_password(user['password_hash'], password):
            print("VERIFICATION: Password check PASSED.")
        else:
            print("VERIFICATION: Password check FAILED.")
    else:
        print("VERIFICATION: User NOT found.")
    conn.close()

if __name__ == "__main__":
    setup()
