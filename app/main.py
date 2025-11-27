from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db import init_db
from app.api import auth, kyc, admin, dashboard, reports
import os

app = FastAPI(
    title="NeoBank KYC Platform",
    description="High-Security KYC Verification System with AI and Geolocation",
    version="2.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:5173", # React Dev Server
    "http://localhost:3000",
    "https://kycverificationsystem.netlify.app", # Production Frontend (Current)
    "https://guiltless-haupia-b5b8f7.netlify.app", # Production Frontend (Old)
    "*"  # Allow all origins for now
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files for Uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(kyc.router, prefix="/api/kyc", tags=["kyc"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(reports.router, prefix="/api/admin", tags=["reports"])

# Initialize DB and Migrations
@app.on_event("startup")
def on_startup():
    try:
        init_db()
        
        # Run Migrations Safely
        from app.db import get_conn
        import sqlite3
        conn = get_conn()
        cursor = conn.cursor()
        
        # Helper function to add column if missing
        def add_column_safe(table, column, type_def):
            try:
                cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
            except sqlite3.OperationalError:
                print(f"Migrating: Adding '{column}' to {table}...")
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")
                    conn.commit()
                except Exception as e:
                    print(f"Migration Error ({column}): {e}")

        # Customers Table Migrations
        add_column_safe("Customers", "customer_code", "TEXT")
        add_column_safe("Customers", "trust_score", "INTEGER DEFAULT 50")
        add_column_safe("Customers", "segment", "TEXT DEFAULT 'Standard'")

        # Admins Table Migrations
        add_column_safe("Admins", "email", "TEXT")
        add_column_safe("Admins", "role", "TEXT DEFAULT 'admin'")
        add_column_safe("Admins", "totp_secret", "TEXT")
            
        # Ensure Admin Exists
        try:
            admin = cursor.execute("SELECT * FROM Admins WHERE username = 'Asharib'").fetchone()
            if not admin:
                from app import auth
                hashed_pw = auth.hash_password("mywordislaw")
                cursor.execute("INSERT INTO Admins (username, password_hash, full_name, email, role) VALUES (?, ?, ?, ?, ?)", 
                              ("Asharib", hashed_pw, "Asharib Khan", "admin@neobank.com", "admin"))
                conn.commit()
                print("Admin user 'Asharib' created.")
        except Exception as e:
            print(f"Admin Creation Error: {e}")
        
        conn.close()
    except Exception as e:
        print(f"Startup Error: {e}")
        # Don't raise, allow app to start even if migration fails partially

@app.get("/")
def root():
    return {"message": "NeoBank KYC API is running securely."}

@app.get("/api/debug-2fa")
def debug_2fa():
    """
    Debug endpoint to test 2FA sending logic
    """
    try:
        from app import config
        from app.api.auth import OTP_STORE
        import random
        
        username = "Asharib"
        code = str(random.randint(100000, 999999))
        OTP_STORE[username] = code
        
        results = {"steps": []}
        
        # 1. Test Twilio
        try:
            from twilio.rest import Client
            results["steps"].append("Twilio module imported")
            
            client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            results["steps"].append("Twilio client initialized")
            
            message = client.messages.create(
                from_=config.TWILIO_WHATSAPP_FROM,
                body=f"🔐 Debug Code: {code}",
                to=config.ADMIN_WHATSAPP_NUMBER
            )
            results["steps"].append(f"Twilio message sent: {message.sid}")
            results["twilio_success"] = True
        except Exception as e:
            results["twilio_error"] = str(e)
            results["twilio_success"] = False
            
        return results
    except Exception as e:
        import traceback
        return {
            "error": "Debug failed",
            "detail": str(e),
            "traceback": traceback.format_exc()
        }
