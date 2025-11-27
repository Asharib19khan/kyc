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

# Initialize DB
@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "NeoBank KYC API is running securely."}

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(kyc.router, prefix="/api/kyc", tags=["kyc"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(reports.router, prefix="/api/admin", tags=["reports"])

# TEMPORARY: Initialize first admin user (remove after first run)
@app.get("/api/init-admin")
def initialize_admin():
    """
    ONE-TIME USE: Creates the first admin user
    Visit this URL once after deployment to create admin account
    """
    try:
        # Debug imports
        import sys
        import os
        
        # Try importing auth
        try:
            from app import auth
        except ImportError as e:
            return {"error": f"ImportError app.auth: {str(e)}", "path": sys.path, "cwd": os.getcwd()}
            
        # Try importing db
        try:
            from app.db import get_conn
        except ImportError as e:
            return {"error": f"ImportError app.db: {str(e)}"}
        
        conn = get_conn()
        cursor = conn.cursor()
        
        # Check if admin already exists
        existing = cursor.execute("SELECT * FROM Admins WHERE username = ?", ("Asharib",)).fetchone()
        if existing:
            conn.close()
            return {"error": "Admin user already exists"}
        
        # Create admin user using auth module
        username = "Asharib"
        password = "mywordislaw"
        full_name = "Asharib Khan"
        email = "asharib@neobank.com"
        
        try:
            hashed_password = auth.hash_password(password)
        except Exception as e:
            conn.close()
            return {"error": f"Hashing failed: {str(e)}"}
        
        # Handle Schema Migration (Add missing columns if needed)
        try:
            cursor.execute("SELECT email FROM Admins LIMIT 1")
        except Exception:
            # Column email missing, add it
            try:
                cursor.execute("ALTER TABLE Admins ADD COLUMN email TEXT")
                conn.commit()
            except Exception as e:
                return {"error": f"Failed to add email column: {str(e)}"}

        try:
            cursor.execute("SELECT role FROM Admins LIMIT 1")
        except Exception:
            # Column role missing, add it
            try:
                cursor.execute("ALTER TABLE Admins ADD COLUMN role TEXT DEFAULT 'super_admin'")
                conn.commit()
            except Exception as e:
                return {"error": f"Failed to add role column: {str(e)}"}
        
        # Now Insert
        cursor.execute(
            "INSERT INTO Admins (username, password_hash, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_password, full_name, email, "super_admin")
        )
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Admin user created successfully",
            "username": username,
            "note": "You can now login with this username and your password"
        }
    except Exception as e:
        import traceback
        return {
            "error": "Unexpected error",
            "detail": str(e),
            "traceback": traceback.format_exc()
        }

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

