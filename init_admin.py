from app.auth import create_admin
from app.db import init_db

# Initialize DB first
init_db()

# Create Admin
create_admin("admin", "admin123", "System Administrator")
