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
    "https://guiltless-haupia-b5b8f7.netlify.app", # Production Frontend
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

# Initialize DB and create default admin if needed
@app.on_event("startup")
def on_startup():
    init_db()
    
    # Auto-create admin user if it doesn't exist
    from app import auth as app_auth
    from app.db import get_conn
    
    conn = get_conn()
    cursor = conn.cursor()
    
    # Check if any admin exists
    existing_admin = cursor.execute("SELECT username FROM Admins LIMIT 1").fetchone()
    
    if not existing_admin:
        # Create default admin user
        username = "Asharib"
        password = "mywordislaw"
        full_name = "Asharib Khan"
        email = "asharib@neobank.com"
        
        hashed_password = app_auth.hash_password(password)
        
        cursor.execute(
            "INSERT INTO Admins (username, password_hash, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_password, full_name, email, "super_admin")
        )
        conn.commit()
        print(f"✅ Default admin user '{username}' created successfully!")
    
    conn.close()

@app.get("/")
def root():
    return {"message": "NeoBank KYC API is running securely.", "admin_ready": True}

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(kyc.router, prefix="/api/kyc", tags=["kyc"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(reports.router, prefix="/api/admin", tags=["reports"])
