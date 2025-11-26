# How to Change Admin Credentials

To change the admin username and password, you have two options:

## Option 1: Using the Admin Dashboard (Easiest)
1. Login to the Admin App (`run_admin.bat`).
2. Go to the **"Manage Admins"** tab.
3. Create a new Admin user with your desired username and password.
4. You can now login with the new credentials.

## Option 2: Resetting via Script (If you forgot the password)
1. Open `setup.bat` in a text editor (like Notepad).
2. Find the line:
   `python -c "from app import auth; auth.create_admin('admin', 'admin123')"`
3. Change `'admin'` and `'admin123'` to your desired username and password.
4. Run `setup.bat` again.
   *Note: This will try to create the user. If the username already exists, it might error, so use a new username or delete the database file (`data/kyc.sqlite3`) to start fresh.*

## Option 3: Python Console (Advanced)
1. Open a terminal in the project folder.
2. Run `python`.
3. Type the following commands:
   ```python
   from app import auth
   auth.create_admin("new_user", "new_password")
   exit()
   ```
