from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import sqlite3
from app.db import get_conn

# Initialize Argon2id Hasher
# Default parameters are secure: time_cost=3, memory_cost=65536, parallelism=4
ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hashes a password using Argon2id."""
    return ph.hash(password)

def check_password(hashed_password: str, user_password: str) -> bool:
    """Checks a password against an Argon2id hash."""
    try:
        return ph.verify(hashed_password, user_password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False

def create_admin(username, password, full_name="Admin User"):
    """Creates a new admin user with Argon2id hashing."""
    conn = get_conn()
    cursor = conn.cursor()
    
    hashed = hash_password(password)
    
    try:
        cursor.execute(
            "INSERT INTO Admins (username, password_hash, full_name) VALUES (?, ?, ?)",
            (username, hashed, full_name)
        )
        conn.commit()
        print(f"Admin user '{username}' created successfully.")
    except sqlite3.IntegrityError:
        print(f"Error: Admin username '{username}' already exists.")
    except Exception as e:
        print(f"Error creating admin: {e}")
    finally:
        conn.close()
