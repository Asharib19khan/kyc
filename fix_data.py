from app import db

def delete_user(user_id):
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Customers WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    print(f"Deleted User ID {user_id}")

if __name__ == "__main__":
    delete_user(3)
